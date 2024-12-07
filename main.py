from components import (
    RSSFeedFetcher, 
    DataStandardizer, 
    ArticleDatabase, 
    RelevanceScorer, 
    NewsletterComposer,
    LLMOrchestrator,  # new
    MemoryManager,    # new
    EmailSender       # new
)
from typing import List, Dict
import logging
from datetime import datetime
import config  # we'll create this for managing API keys and settings

class SedRSSSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.rss_fetcher = RSSFeedFetcher()
        self.data_standardizer = DataStandardizer()
        self.article_db = ArticleDatabase()
        
        # New LLM components
        self.llm_orchestrator = LLMOrchestrator(
            model_name=config.LLM_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        self.memory_manager = MemoryManager(
            vector_store_path=config.VECTOR_STORE_PATH
        )
        
        # Enhanced scoring and composition
        self.relevance_scorer = RelevanceScorer(
            impact_factors=config.JOURNAL_IMPACT_FACTORS,
            keywords=config.KEYWORDS,
            llm_orchestrator=self.llm_orchestrator
        )
        self.newsletter_composer = NewsletterComposer(
            llm_orchestrator=self.llm_orchestrator,
            memory_manager=self.memory_manager
        )
        
        self.email_sender = EmailSender(
            smtp_config=config.SMTP_CONFIG
        )

    async def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process articles with LLM for enhanced understanding"""
        return await self.llm_orchestrator.process_batch(articles)

    async def run(self):
        try:
            # 1. Fetch and standardize data
            self.logger.info("Fetching RSS feeds...")
            raw_data = await self.rss_fetcher.fetch_all()
            self.logger.info(f"Fetched {len(raw_data)} articles")

            standardized_data = self.data_standardizer.standardize(raw_data)
            self.article_db.store(standardized_data)

            # 2. LLM Processing and Scoring
            articles = self.article_db.get_recent_articles()
            
            self.logger.info("Processing articles with LLM...")
            processed_articles = await self.process_articles(articles)
            
            self.logger.info("Scoring articles...")
            scored_articles = await self.relevance_scorer.score(processed_articles)

            # 3. Update memory system
            self.logger.info("Updating memory system...")
            await self.memory_manager.update(scored_articles)

            # 4. Compose newsletter with context
            self.logger.info("Composing newsletter...")
            newsletter_content = await self.newsletter_composer.compose(
                scored_articles,
                historical_context=await self.memory_manager.get_relevant_context()
            )

            # 5. Send newsletter
            self.logger.info("Sending newsletter...")
            await self.email_sender.send(
                subject=f"SedRSS Newsletter - {datetime.now().strftime('%Y-%m-%d')}",
                content=newsletter_content,
                recipients=config.SUBSCRIBER_LIST
            )

            self.logger.info("Newsletter process complete")

        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            raise

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    sedrss = SedRSSSystem()
    asyncio.run(sedrss.run())