from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from uuid import uuid4
from enum import Enum

router = APIRouter()

# In-memory storage for MVP
reports_db = []


class ReportType(str, Enum):
    FULL = "full"
    CLIMATE = "climate"
    VEGETATION = "vegetation"
    WATER = "water"
    CROP_COMPARISON = "crop_comparison"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportCreate(BaseModel):
    farm_id: str
    title: str = Field(..., min_length=1, max_length=200)
    type: ReportType
    period_start: date
    period_end: date
    sections: List[str] = [
        "executive_summary",
        "climate",
        "vegetation",
        "risks",
        "water",
        "crop_comparison",
        "recommendations",
        "data_sources",
    ]


class ReportResponse(BaseModel):
    id: str
    farm_id: str
    title: str
    type: ReportType
    status: ReportStatus
    period_start: date
    period_end: date
    sections: List[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int


async def generate_report_background(report_id: str):
    """Background task to generate report"""
    report = next((r for r in reports_db if r.id == report_id), None)
    if not report:
        return

    report.status = ReportStatus.GENERATING

    # Simulate report generation
    import asyncio
    await asyncio.sleep(3)

    # Mock result
    report.status = ReportStatus.COMPLETED
    report.completed_at = datetime.utcnow()
    report.file_size = 2400000  # 2.4 MB
    report.page_count = 12
    report.download_url = f"/api/reports/{report_id}/download"


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(report: ReportCreate, background_tasks: BackgroundTasks):
    """Create a new report generation job"""
    new_report = ReportResponse(
        id=str(uuid4()),
        **report.model_dump(),
        status=ReportStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    reports_db.append(new_report)

    # Start background generation
    background_tasks.add_task(generate_report_background, new_report.id)

    return new_report


@router.get("", response_model=ReportListResponse)
async def list_reports(
    farm_id: Optional[str] = None,
    type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List reports with optional filters"""
    filtered = reports_db

    if farm_id:
        filtered = [r for r in filtered if r.farm_id == farm_id]
    if type:
        filtered = [r for r in filtered if r.type == type]
    if status:
        filtered = [r for r in filtered if r.status == status]

    # Sort by created_at descending
    filtered.sort(key=lambda r: r.created_at, reverse=True)

    total = len(filtered)
    reports = filtered[skip:skip + limit]
    return ReportListResponse(reports=reports, total=total)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Get report details"""
    report = next((r for r in reports_db if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Download generated report PDF"""
    report = next((r for r in reports_db if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Rapport pas encore généré")

    # In real app, would return actual PDF file
    # For MVP, return a placeholder response
    return {
        "message": "PDF download would start here",
        "report_id": report_id,
        "filename": f"{report.title.replace(' ', '_')}.pdf",
        "content_type": "application/pdf",
    }


@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str):
    """Delete a report"""
    global reports_db
    report = next((r for r in reports_db if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    reports_db = [r for r in reports_db if r.id != report_id]


@router.get("/types/list")
async def get_report_types():
    """Get available report types"""
    return [
        {
            "type": ReportType.FULL,
            "label": "Diagnostic complet",
            "description": "Rapport complet incluant climat, végétation, eau, risques, cultures et recommandations",
            "estimated_pages": 10,
            "estimated_time_seconds": 30,
        },
        {
            "type": ReportType.CLIMATE,
            "label": "Analyse climatique",
            "description": "Analyse détaillée des températures, précipitations et variables climatiques",
            "estimated_pages": 6,
            "estimated_time_seconds": 15,
        },
        {
            "type": ReportType.VEGETATION,
            "label": "Suivi végétale",
            "description": "Évolution du NDVI, détection d'anomalies, comparaison multi-périodes",
            "estimated_pages": 5,
            "estimated_time_seconds": 15,
        },
        {
            "type": ReportType.WATER,
            "label": "Ressources en eau",
            "description": "Précipitations, humidité des sols, bilan hydrique, risques de sécheresse",
            "estimated_pages": 5,
            "estimated_time_seconds": 15,
        },
        {
            "type": ReportType.CROP_COMPARISON,
            "label": "Comparaison cultures",
            "description": "Évaluation comparative de plusieurs cultures selon l'adéquation pédoclimatique",
            "estimated_pages": 5,
            "estimated_time_seconds": 10,
        },
    ]


@router.post("/preview")
async def preview_report(report: ReportCreate):
    """Generate a preview of the report structure"""
    sections_info = {
        "executive_summary": {"title": "Résumé exécutif", "pages": 1, "required": True},
        "climate": {"title": "Conditions climatiques", "pages": 2, "required": True},
        "vegetation": {"title": "État de la végétation (NDVI)", "pages": 2, "required": False},
        "risks": {"title": "Analyse des risques", "pages": 1, "required": True},
        "water": {"title": "Ressources en eau", "pages": 1, "required": False},
        "crop_comparison": {"title": "Comparaison des cultures", "pages": 2, "required": False},
        "recommendations": {"title": "Recommandations d'adaptation", "pages": 1, "required": True},
        "data_sources": {"title": "Sources et limites des données", "pages": 1, "required": True},
    }

    selected_sections = [s for s in report.sections if s in sections_info]
    total_pages = sum(sections_info[s]["pages"] for s in selected_sections)
    estimated_time = sum(5 for s in selected_sections)  # rough estimate

    return {
        "title": report.title,
        "farm_id": report.farm_id,
        "period": f"{report.period_start} à {report.period_end}",
        "sections": [
            {
                "id": s,
                "title": sections_info[s]["title"],
                "pages": sections_info[s]["pages"],
                "included": s in report.sections,
            }
            for s in sections_info
        ],
        "estimated_total_pages": total_pages,
        "estimated_generation_time_seconds": estimated_time,
    }