"""
Database Initialization Script
Creates tables and seeds initial data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import engine, Base
from backend.models.database import DataSource, CollectedData, Analysis, Report, Alert
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    logger.info("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Optional: Add sample data
        add_sample_data()
        
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


def add_sample_data():
    """Add sample data sources for demonstration"""
    logger.info("Adding sample data...")
    
    session = Session(engine)
    
    try:
        # Check if data already exists
        existing = session.query(DataSource).first()
        if existing:
            logger.info("Sample data already exists, skipping...")
            return
        
        # Add sample GitHub source
        github_source = DataSource(
            name="Kubernetes Repository",
            source_type="github",
            config={
                "token": "your_github_token_here",
                "repositories": ["kubernetes/kubernetes"]
            },
            enabled=False,  # Disabled by default until token is configured
            check_interval=600
        )
        session.add(github_source)
        
        # Add another sample
        sample_source = DataSource(
            name="TensorFlow Repository",
            source_type="github",
            config={
                "token": "your_github_token_here",
                "repositories": ["tensorflow/tensorflow"]
            },
            enabled=False,
            check_interval=600
        )
        session.add(sample_source)
        
        session.commit()
        logger.info("✅ Sample data added successfully")
        logger.info("⚠️  Remember to configure GitHub tokens in your data sources!")
        
    except Exception as e:
        logger.error(f"❌ Error adding sample data: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("=== OSInt-AI Database Initialization ===")
    init_database()
    logger.info("=== Initialization Complete ===")
