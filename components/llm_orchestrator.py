from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import asyncio
import json

class LLMOrchestrator:
    def __init__(self, model_name: str, api_key: str):
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            temperature=0.3
        )
        
        self._init_prompts()
        self._init_output_parsers()
        
    def _init_output_parsers(self):
        """Initialize output parsers for structured responses"""
        relevance_schemas = [
            ResponseSchema(name="relevance_score", 
                         description="Float between 0-1 indicating relevance"),
            ResponseSchema(name="key_topics", 
                         description="List of key topics from the article"),
            ResponseSchema(name="reasoning", 
                         description="Explanation of the relevance score")
        ]
        self.relevance_parser = StructuredOutputParser.from_response_schemas(relevance_schemas)
        
    def _init_prompts(self):
        """Initialize various prompts used by the orchestrator"""
        self.summary_prompt = ChatPromptTemplate.from_template(
            """You are an expert in sedimentology and geomorphology. 
            Summarize this scientific article for researchers in the field:
            
            Title: {title}
            Abstract: {abstract}
            
            Focus on:
            1. Key findings and their significance
            2. Methodology highlights
            3. Implications for sedimentology and geomorphology
            
            Keep the summary technical but concise (150 words max).
            Highlight any novel approaches or unexpected results."""
        )
        
        self.relevance_prompt = ChatPromptTemplate.from_template(
            """Evaluate this article's relevance to sedimentology and fluvial geomorphology:
            
            Title: {title}
            Summary: {summary}
            
            Consider these key areas: {keywords}
            
            Format your response as JSON with:
            {format_instructions}
            
            Base the relevance score on:
            - Direct applicability to sedimentology/geomorphology
            - Methodological innovation
            - Potential impact on the field
            """
        )
        
    async def process_batch(self, articles: List[Dict]) -> List[Dict]:
        """Process a batch of articles with parallel LLM calls"""
        tasks = []
        for article in articles:
            tasks.append(self.process_single(article))
        
        return await asyncio.gather(*tasks)
    
    async def process_single(self, article: Dict) -> Dict:
        """Process a single article with LLM analysis"""
        # Create chains
        summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
        relevance_chain = LLMChain(llm=self.llm, prompt=self.relevance_prompt)
        
        # Generate summary
        summary_result = await summary_chain.arun(
            title=article['title'],
            abstract=article['abstract']
        )
        article['llm_summary'] = summary_result
        
        # Generate relevance analysis
        relevance_result = await relevance_chain.arun(
            title=article['title'],
            summary=summary_result,
            keywords=", ".join(article.get('keywords', [])),
            format_instructions=self.relevance_parser.get_format_instructions()
        )
        
        try:
            parsed_relevance = self.relevance_parser.parse(relevance_result)
            article.update({
                'relevance_score': float(parsed_relevance['relevance_score']),
                'key_topics': parsed_relevance['key_topics'],
                'relevance_reasoning': parsed_relevance['reasoning']
            })
        except Exception as e:
            article.update({
                'relevance_score': 0.0,
                'key_topics': [],
                'relevance_reasoning': f"Error parsing relevance: {str(e)}"
            })
        
        return article

    async def get_article_highlights(self, articles: List[Dict], n_highlights: int = 3) -> str:
        """Generate engaging highlights for the newsletter"""
        highlights_prompt = ChatPromptTemplate.from_template(
            """Create engaging highlights for these top articles in sedimentology:
            
            Articles:
            {article_summaries}
            
            Write 2-3 sentences for each article that:
            1. Capture the most interesting finding
            2. Explain why it matters to the field
            3. Use engaging, professional language
            
            Format as markdown with article titles as headers."""
        )
        
        # Sort by relevance and take top n
        sorted_articles = sorted(articles, 
                               key=lambda x: x.get('relevance_score', 0), 
                               reverse=True)[:n_highlights]
        
        summaries = "\n\n".join([
            f"Title: {a['title']}\nSummary: {a['llm_summary']}\n"
            f"Key Topics: {', '.join(a['key_topics'])}"
            for a in sorted_articles
        ])
        
        highlights_chain = LLMChain(llm=self.llm, prompt=highlights_prompt)
        return await highlights_chain.arun(article_summaries=summaries)