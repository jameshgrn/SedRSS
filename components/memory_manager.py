from typing import List, Dict, Optional
import json
import os
from datetime import datetime, timedelta
import duckdb

class MemoryManager:
    def __init__(self, db_path: str = "data/newsletter.ddb"):
        """Initialize with DuckDB for efficient storage and querying"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize DuckDB database"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id VARCHAR PRIMARY KEY,
                title VARCHAR,
                journal VARCHAR,
                published_date TIMESTAMP,
                relevance_score DOUBLE,
                summary VARCHAR,
                processed_date TIMESTAMP
            )
        """)
    
    async def update(self, articles: List[Dict]) -> None:
        """Store new articles in DuckDB using efficient batch insert"""
        if not articles:
            return
            
        # Create a temporary table for the batch insert
        self.conn.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_articles (
                id VARCHAR,
                title VARCHAR,
                journal VARCHAR,
                published_date TIMESTAMP,
                relevance_score DOUBLE,
                summary VARCHAR,
                processed_date TIMESTAMP
            )
        """)
        
        # Convert articles to tuples for batch insert
        values = [
            (
                self._generate_article_id(article),
                article['title'],
                article.get('journal', ''),
                article['published_date'],
                float(article.get('relevance_score', 0.0)),
                article.get('llm_summary', ''),
                datetime.now().isoformat()
            )
            for article in articles
        ]
        
        # Batch insert into temporary table
        self.conn.executemany("""
            INSERT INTO temp_articles 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, values)
        
        # Use UPSERT to handle duplicates efficiently
        self.conn.execute("""
            INSERT OR REPLACE INTO articles 
            SELECT * FROM temp_articles
        """)
        
        # Cleanup temporary table
        self.conn.execute("DROP TABLE temp_articles")
    
    def _generate_article_id(self, article: Dict) -> str:
        """Generate a unique ID for the article"""
        unique_string = f"{article['title']}-{article['published_date']}"
        return str(hash(unique_string))
    
    async def get_relevant_context(self, 
                                 n_results: int = 5,
                                 days_back: int = 14) -> List[Dict]:
        """Get recent relevant articles using efficient date filtering"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # Use parameterized query for safety and efficiency
        result = self.conn.execute("""
            SELECT *
            FROM articles 
            WHERE published_date >= ?
                AND relevance_score IS NOT NULL  -- Optimization for NULL handling
            ORDER BY relevance_score DESC
            LIMIT ?
        """, [cutoff_date, n_results]).fetchall()
        
        # Convert to list of dicts
        columns = ['id', 'title', 'journal', 'published_date', 
                  'relevance_score', 'summary', 'processed_date']
        return [dict(zip(columns, row)) for row in result]
    
    async def cleanup_old_entries(self, days: int = 90) -> None:
        """Remove entries older than specified days using efficient batch delete"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        self.conn.execute("""
            DELETE FROM articles 
            WHERE processed_date < ?
        """, [cutoff_date])
    
    def __del__(self):
        """Ensure connection is closed properly"""
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
            except:
                pass  # Ignore errors during cleanup