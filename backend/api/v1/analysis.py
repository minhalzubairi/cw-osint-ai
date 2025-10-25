"""
Analysis API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.database import get_db
from models.database import Analysis, DataSource, CollectedData
from analyzers.ai_analyzer import AIAnalyzer

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for triggering analysis"""
    source_id: int = None
    data_ids: List[int] = None
    analysis_type: str = "comprehensive"  # sentiment, trend, summary, comprehensive


class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    id: int
    source_id: int
    data_id: int = None
    analysis_type: str
    result: Dict[str, Any]
    confidence: float = None
    model_used: str = None
    processing_time: float = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/analyze", response_model=List[AnalysisResponse])
async def analyze_data(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger AI analysis on collected data
    
    - **source_id**: Analyze all data from a specific source
    - **data_ids**: Analyze specific data entries
    - **analysis_type**: Type of analysis to perform
    """
    
    # Get data to analyze
    if request.data_ids:
        data_items = db.query(CollectedData).filter(
            CollectedData.id.in_(request.data_ids)
        ).all()
    elif request.source_id:
        # Get recent data from source (last 24 hours)
        since = datetime.utcnow() - timedelta(hours=24)
        data_items = db.query(CollectedData).filter(
            CollectedData.source_id == request.source_id,
            CollectedData.collected_at >= since
        ).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either source_id or data_ids must be provided"
        )
    
    if not data_items:
        return []
    
    # Perform analysis
    analyzer = AIAnalyzer()
    analyses = []
    
    for data in data_items:
        try:
            result = await analyzer.analyze(
                content=data.content,
                analysis_type=request.analysis_type,
                metadata=data.metadata
            )
            
            analysis = Analysis(
                source_id=data.source_id,
                data_id=data.id,
                analysis_type=request.analysis_type,
                result=result,
                confidence=result.get('confidence'),
                model_used=result.get('model'),
                processing_time=result.get('processing_time')
            )
            
            db.add(analysis)
            analyses.append(analysis)
        except Exception as e:
            # Log error but continue with other items
            print(f"Analysis failed for data {data.id}: {e}")
    
    db.commit()
    
    # Refresh to get IDs
    for analysis in analyses:
        db.refresh(analysis)
    
    return analyses


@router.get("/results", response_model=List[AnalysisResponse])
async def get_analysis_results(
    source_id: int = None,
    analysis_type: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get analysis results with optional filtering
    """
    query = db.query(Analysis)
    
    if source_id:
        query = query.filter(Analysis.source_id == source_id)
    
    if analysis_type:
        query = query.filter(Analysis.analysis_type == analysis_type)
    
    analyses = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get a specific analysis result
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    return analysis


@router.get("/source/{source_id}/trends")
async def get_source_trends(
    source_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get trend analysis for a specific source
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    analyses = db.query(Analysis).filter(
        Analysis.source_id == source_id,
        Analysis.analysis_type.in_(['trend', 'comprehensive']),
        Analysis.created_at >= since
    ).all()
    
    # Aggregate trends
    trends = {}
    for analysis in analyses:
        result = analysis.result
        if 'trends' in result:
            for trend in result['trends']:
                topic = trend.get('topic')
                if topic not in trends:
                    trends[topic] = {
                        'topic': topic,
                        'mentions': 0,
                        'avg_sentiment': 0,
                        'occurrences': []
                    }
                trends[topic]['mentions'] += trend.get('mentions', 1)
                trends[topic]['occurrences'].append({
                    'timestamp': analysis.created_at.isoformat(),
                    'sentiment': trend.get('sentiment', 'neutral')
                })
    
    return {
        "source_id": source_id,
        "period_days": days,
        "trends": list(trends.values()),
        "generated_at": datetime.utcnow().isoformat()
    }
