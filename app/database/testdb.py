import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.models import WHOArticle
from app.database.connection import engine, get_session

def create_tables():
    """Create the WHO articles table"""
    WHOArticle.metadata.create_all(engine)
    print(f"✓ Table 'who_articles' created successfully")

def add_sample_data():
    """Add sample WHO news articles for testing"""
    session = get_session()
    
    # Sample data
    sample_articles = [
        {
            "article_id": "who-2024-001",
            "title": "WHO launches new initiative to combat global health threats",
            "url": "https://www.who.int/news/item/2024-01-15-who-launches-new-initiative",
            "release_date": datetime.now() - timedelta(days=1),
            "news_type": "News release",
            "word_count": "450",
            "full_text": "The World Health Organization today announced a new global initiative aimed at strengthening health systems worldwide. This comprehensive program will focus on improving disease surveillance, enhancing emergency response capabilities, and building resilient healthcare infrastructure in resource-limited settings. The initiative represents a significant step forward in global health security and pandemic preparedness."
        },
        {
            "article_id": "who-2024-002",
            "title": "New guidelines published for maternal and child health care",
            "url": "https://www.who.int/news/item/2024-01-14-maternal-child-health-guidelines",
            "release_date": datetime.now() - timedelta(days=2),
            "news_type": "Guidelines",
            "word_count": "680",
            "full_text": "The World Health Organization has released updated guidelines for maternal and child health care, emphasizing evidence-based practices and community-centered approaches. These guidelines provide healthcare workers with the latest recommendations for prenatal care, safe delivery practices, and postnatal support. The document includes new sections on mental health support for new mothers and strategies for reducing maternal mortality in low-resource settings."
        },
        {
            "article_id": "who-2024-003",
            "title": "Global vaccination campaign reaches milestone",
            "url": "https://www.who.int/news/item/2024-01-13-vaccination-milestone",
            "release_date": datetime.now() - timedelta(days=3),
            "news_type": "Feature story",
            "word_count": "520",
            "full_text": "A major global vaccination campaign has reached a significant milestone, with over 2 billion doses administered across 150 countries. This achievement represents unprecedented collaboration between governments, international organizations, and local communities. The campaign has been particularly successful in reaching remote and underserved populations, demonstrating the power of coordinated global health efforts."
        },
        {
            "article_id": "who-2024-004",
            "title": "WHO responds to disease outbreak in Southeast Asia",
            "url": "https://www.who.int/news/item/2024-01-12-disease-outbreak-response",
            "release_date": datetime.now() - timedelta(days=4),
            "news_type": "News release",
            "word_count": None,  # Testing null word_count
            "full_text": "The World Health Organization is coordinating an emergency response to a disease outbreak in Southeast Asia. Rapid response teams have been deployed to affected areas, and surveillance systems are being strengthened. The organization is working closely with local health authorities to contain the outbreak and provide necessary medical supplies and expertise."
        },
        {
            "article_id": "who-2024-005",
            "title": "New research highlights importance of clean water access",
            "url": "https://www.who.int/news/item/2024-01-11-clean-water-research",
            "release_date": datetime.now() - timedelta(days=5),
            "news_type": "Research",
            "word_count": "750",
            "full_text": "A comprehensive new study published by WHO researchers highlights the critical importance of clean water access for public health. The research, conducted across multiple countries, demonstrates clear links between water quality and disease prevention. Findings show that improving water infrastructure can reduce waterborne diseases by up to 40% in affected communities. The study provides evidence-based recommendations for policymakers and public health officials."
        }
    ]
    
    try:
        for article_data in sample_articles:
            # Check if article already exists
            existing = session.query(WHOArticle).filter_by(article_id=article_data["article_id"]).first()
            if existing:
                print(f"⚠ Article {article_data['article_id']} already exists, skipping...")
                continue
            
            article = WHOArticle(**article_data)
            session.add(article)
        
        session.commit()
        print(f"✓ Added {len(sample_articles)} sample articles to database")
        
        # Display summary
        total = session.query(WHOArticle).count()
        print(f"✓ Total articles in database: {total}")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error adding sample data: {e}")
        raise
    finally:
        session.close()

def display_articles():
    """Display all articles in the database"""
    session = get_session()
    try:
        articles = session.query(WHOArticle).order_by(WHOArticle.release_date.desc()).all()
        print("\n" + "="*80)
        print("ARTICLES IN DATABASE")
        print("="*80)
        for article in articles:
            print(f"\nID: {article.article_id}")
            print(f"Title: {article.title}")
            print(f"URL: {article.url}")
            print(f"Release Date: {article.release_date}")
            print(f"News Type: {article.news_type}")
            print(f"Word Count: {article.word_count or 'N/A'}")
            print(f"Full Text (first 100 chars): {article.full_text[:100] if article.full_text else 'N/A'}...")
            print(f"Created At: {article.created_at}")
            print("-"*80)
    finally:
        session.close()

if __name__ == "__main__":
    print("Creating WHO News Database...")
    print("="*80)
    
    # Create tables
    create_tables()
    
    # Add sample data
    print("\nAdding sample data...")
    add_sample_data()
    
    # Display articles
    display_articles()
    
    print("\n" + "="*80)
    print("Database setup complete!")
    print(f"Database location: {engine.url}")
    print("="*80)

