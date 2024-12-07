import pytest
from datetime import datetime, timedelta
import os
from components.memory_manager import MemoryManager

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path"""
    return str(tmp_path / "test_newsletter.ddb")

@pytest.fixture
def memory_manager(test_db_path):
    """Create a test memory manager instance"""
    manager = MemoryManager(test_db_path)
    yield manager
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def sample_articles():
    """Create sample article data"""
    return [
        {
            'title': 'Test Article 1',
            'journal': 'Nature',
            'published_date': datetime.now().isoformat(),
            'relevance_score': 0.9,
            'llm_summary': 'This is a test summary 1'
        },
        {
            'title': 'Test Article 2',
            'journal': 'Science',
            'published_date': (datetime.now() - timedelta(days=5)).isoformat(),
            'relevance_score': 0.7,
            'llm_summary': 'This is a test summary 2'
        }
    ]

@pytest.mark.asyncio
async def test_update_and_retrieve(memory_manager, sample_articles):
    """Test storing and retrieving articles"""
    await memory_manager.update(sample_articles)
    
    # Get recent articles
    results = await memory_manager.get_relevant_context(n_results=2)
    
    assert len(results) == 2
    assert results[0]['title'] == 'Test Article 1'  # Higher relevance score
    assert results[1]['title'] == 'Test Article 2'
    assert float(results[0]['relevance_score']) == 0.9

@pytest.mark.asyncio
async def test_cleanup_old_entries(memory_manager, sample_articles):
    """Test cleaning up old entries"""
    # Add old article
    old_article = {
        'title': 'Old Article',
        'journal': 'Old Journal',
        'published_date': (datetime.now() - timedelta(days=100)).isoformat(),
        'relevance_score': 0.5,
        'llm_summary': 'Old summary'
    }
    
    all_articles = sample_articles + [old_article]
    await memory_manager.update(all_articles)
    
    # Clean up articles older than 30 days
    await memory_manager.cleanup_old_entries(days=30)
    
    # Should only get recent articles
    results = await memory_manager.get_relevant_context(n_results=10)
    assert len(results) == 2
    assert all(r['title'] != 'Old Article' for r in results) 