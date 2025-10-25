"""
Data Sources API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from backend.core.database import get_db
from backend.models.database import DataSource
from backend.collectors.factory import CollectorFactory

router = APIRouter()


# Pydantic models for request/response
class DataSourceCreate(BaseModel):
    """Request model for creating a data source"""
    name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., description="Type of data source (github, rss, etc.)")
    config: Dict[str, Any] = Field(..., description="Source-specific configuration")
    enabled: bool = True
    check_interval: int = Field(default=300, ge=60, description="Check interval in seconds")


class DataSourceUpdate(BaseModel):
    """Request model for updating a data source"""
    name: str = None
    config: Dict[str, Any] = None
    enabled: bool = None
    check_interval: int = Field(default=None, ge=60)


class DataSourceResponse(BaseModel):
    """Response model for data source"""
    id: int
    name: str
    source_type: str
    config: Dict[str, Any]
    enabled: bool
    check_interval: int
    last_checked: datetime = None
    created_at: datetime
    updated_at: datetime = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[DataSourceResponse])
async def list_sources(
    skip: int = 0,
    limit: int = 100,
    source_type: str = None,
    enabled: bool = None,
    db: Session = Depends(get_db)
):
    """
    List all data sources with optional filtering
    
    - **skip**: Number of sources to skip (pagination)
    - **limit**: Maximum number of sources to return
    - **source_type**: Filter by source type
    - **enabled**: Filter by enabled status
    """
    query = db.query(DataSource)
    
    if source_type:
        query = query.filter(DataSource.source_type == source_type)
    
    if enabled is not None:
        query = query.filter(DataSource.enabled == enabled)
    
    sources = query.offset(skip).limit(limit).all()
    return sources


@router.get("/{source_id}", response_model=DataSourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """
    Get a specific data source by ID
    """
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    return source


@router.post("", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: DataSourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new data source
    
    Validates the configuration and creates a new data source
    """
    # Validate source type
    if source_data.source_type not in CollectorFactory.get_available_collectors():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Available types: {', '.join(CollectorFactory.get_available_collectors())}"
        )
    
    # Create new source
    source = DataSource(
        name=source_data.name,
        source_type=source_data.source_type,
        config=source_data.config,
        enabled=source_data.enabled,
        check_interval=source_data.check_interval
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return source


@router.patch("/{source_id}", response_model=DataSourceResponse)
async def update_source(
    source_id: int,
    source_data: DataSourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing data source
    """
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    
    # Update fields if provided
    update_data = source_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    
    source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """
    Delete a data source
    """
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    
    db.delete(source)
    db.commit()
    
    return None


@router.post("/{source_id}/test")
async def test_source(source_id: int, db: Session = Depends(get_db)):
    """
    Test a data source connection and configuration
    """
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    
    try:
        # Create collector instance
        collector = CollectorFactory.create_collector(source.source_type, source.config)
        
        # Test connection
        test_result = await collector.test_connection()
        
        return {
            "status": "success" if test_result else "failed",
            "message": "Connection test successful" if test_result else "Connection test failed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/{source_id}/collect")
async def trigger_collection(source_id: int, db: Session = Depends(get_db)):
    """
    Manually trigger data collection for a source
    """
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with ID {source_id} not found"
        )
    
    if not source.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot collect from disabled source"
        )
    
    try:
        # Create collector and collect data
        collector = CollectorFactory.create_collector(source.source_type, source.config)
        collected_count = await collector.collect(db, source)
        
        # Update last checked timestamp
        source.last_checked = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "collected": collected_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection failed: {str(e)}"
        )
