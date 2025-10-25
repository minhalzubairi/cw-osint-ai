"""
Database models for OSInt-AI
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from  core.database import Base


class DataSource(Base):
    """Data source configuration model"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # github, rss, twitter, etc.
    config = Column(JSON, nullable=False)  # Source-specific configuration
    enabled = Column(Boolean, default=True)
    check_interval = Column(Integer, default=300)  # seconds
    last_checked = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    collected_data = relationship("CollectedData", back_populates="source")
    analyses = relationship("Analysis", back_populates="source")


class CollectedData(Base):
    """Collected data from sources"""
    __tablename__ = "collected_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # commit, issue, pr, article, etc.
    external_id = Column(String(255), nullable=True)  # External identifier from source
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional metadata
    url = Column(String(1000), nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source = relationship("DataSource", back_populates="collected_data")
    analyses = relationship("Analysis", back_populates="data")


class Analysis(Base):
    """AI analysis results"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    data_id = Column(Integer, ForeignKey("collected_data.id"), nullable=True)
    analysis_type = Column(String(50), nullable=False)  # sentiment, trend, summary, etc.
    result = Column(JSON, nullable=False)  # Analysis results
    confidence = Column(Float, nullable=True)  # Confidence score
    model_used = Column(String(100), nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source = relationship("DataSource", back_populates="analyses")
    data = relationship("CollectedData", back_populates="analyses")


class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, custom
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=True)
    insights = Column(JSON, nullable=False)  # Key insights and findings
    metadata = Column(JSON, nullable=True)  # Additional metadata
    file_path = Column(String(500), nullable=True)  # Path to generated report file
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    """System alerts and notifications"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # anomaly, threshold, error
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    source_info = Column(JSON, nullable=True)  # Information about the source
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
