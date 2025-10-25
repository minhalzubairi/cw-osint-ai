"""
Reports API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.database import Report, Analysis, CollectedData
from backend.utils.report_generator import ReportGenerator

router = APIRouter()


class ReportCreate(BaseModel):
    """Request model for creating a report"""
    title: str
    report_type: str = "custom"  # daily, weekly, monthly, custom
    period_start: datetime
    period_end: datetime
    source_ids: List[int] = None


class ReportResponse(BaseModel):
    """Response model for report"""
    id: int
    title: str
    report_type: str
    period_start: datetime
    period_end: datetime
    summary: str = None
    insights: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """
    Generate a new report for the specified time period
    """
    
    # Get data and analyses for the period
    query = db.query(Analysis).filter(
        Analysis.created_at >= report_data.period_start,
        Analysis.created_at <= report_data.period_end
    )
    
    if report_data.source_ids:
        query = query.filter(Analysis.source_id.in_(report_data.source_ids))
    
    analyses = query.all()
    
    if not analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analyses found for the specified period"
        )
    
    # Generate report insights
    generator = ReportGenerator()
    insights = generator.generate_insights(analyses)
    summary = generator.generate_summary(insights)
    
    # Create report
    report = Report(
        title=report_data.title,
        report_type=report_data.report_type,
        period_start=report_data.period_start,
        period_end=report_data.period_end,
        summary=summary,
        insights=insights
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    report_type: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all generated reports
    """
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/latest", response_model=ReportResponse)
async def get_latest_report(report_type: str = None, db: Session = Depends(get_db)):
    """
    Get the most recent report
    """
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    report = query.order_by(Report.created_at.desc()).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reports found"
        )
    
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get a specific report by ID
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report


@router.get("/{report_id}/export")
async def export_report(
    report_id: int,
    format: str = "json",  # json, pdf, html
    db: Session = Depends(get_db)
):
    """
    Export report in specified format
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    generator = ReportGenerator()
    
    if format == "json":
        return report.insights
    elif format == "pdf":
        pdf_content = generator.export_pdf(report)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
        )
    elif format == "html":
        html_content = generator.export_html(report)
        return Response(
            content=html_content,
            media_type="text/html"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Use json, pdf, or html"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    Delete a report
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    db.delete(report)
    db.commit()
    
    return None
