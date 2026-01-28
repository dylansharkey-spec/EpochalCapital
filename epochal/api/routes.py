"""
API routes for Epochal Capital.

Provides RESTful endpoints for all platform operations.
"""

from datetime import datetime
from typing import Optional

try:
    from fastapi import APIRouter, HTTPException, Query, Depends
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Stub classes for when FastAPI is not installed
    class APIRouter:
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def put(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def delete(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def include_router(self, *args, **kwargs):
            pass

    class BaseModel:
        pass

    def Field(*args, **kwargs):
        return None

    def Query(*args, **kwargs):
        return None

    def Depends(*args, **kwargs):
        return None

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail


from epochal.database import DatabaseManager


# Pydantic models for API
class CompanyCreate(BaseModel):
    """Schema for creating a company."""
    id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Company name")
    description: Optional[str] = None
    vertical: Optional[str] = None
    stage: Optional[str] = None
    valuation_usd: Optional[float] = None
    revenue_arr_usd: Optional[float] = None
    key_investors: Optional[list[str]] = None
    liquidity_signals: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = None
    description: Optional[str] = None
    vertical: Optional[str] = None
    stage: Optional[str] = None
    valuation_usd: Optional[float] = None
    revenue_arr_usd: Optional[float] = None
    risk_score: Optional[float] = None
    thesis_score: Optional[float] = None
    notes: Optional[str] = None


class DealCreate(BaseModel):
    """Schema for creating a deal."""
    id: str = Field(..., description="Unique deal identifier")
    company_id: str = Field(..., description="Associated company ID")
    deal_type: str = Field(..., description="Deal type (secondary, primary, spv, fund)")
    status: str = Field(default="sourcing")
    source: Optional[str] = None
    price_per_share_usd: Optional[float] = None
    total_available_usd: Optional[float] = None
    minimum_usd: Optional[float] = None
    platform: Optional[str] = None
    notes: Optional[str] = None


class DealStatusUpdate(BaseModel):
    """Schema for updating deal status."""
    status: str = Field(..., description="New status")


class InvestmentCreate(BaseModel):
    """Schema for creating an investment."""
    id: str = Field(..., description="Unique investment identifier")
    company_id: str = Field(..., description="Associated company ID")
    deal_id: Optional[str] = None
    investment_type: str = Field(..., description="Investment type")
    status: str = Field(default="active")
    investment_date: Optional[datetime] = None
    shares: Optional[float] = None
    price_per_share_usd: Optional[float] = None
    cost_basis_usd: float = Field(..., description="Total cost basis")


class InvestmentValueUpdate(BaseModel):
    """Schema for updating investment value."""
    current_value_usd: float = Field(..., description="Current value")


class AlertCreate(BaseModel):
    """Schema for creating an alert."""
    id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Alert type")
    priority: str = Field(default="medium")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    company_name: Optional[str] = None
    data: Optional[dict] = None
    tags: Optional[list[str]] = None


class ResearchCreate(BaseModel):
    """Schema for creating research record."""
    company_id: str = Field(..., description="Associated company ID")
    research_type: str = Field(default="valuation")
    valuation_usd: Optional[float] = None
    revenue_arr_usd: Optional[float] = None
    key_findings: Optional[list[str]] = None
    sources: Optional[list[str]] = None
    risk_signals: Optional[list[str]] = None
    liquidity_signals: Optional[list[str]] = None


# Create router
router = APIRouter()


# Dependency for database manager
def get_db() -> DatabaseManager:
    """Get database manager instance."""
    return DatabaseManager()


# =============================================================================
# Company endpoints
# =============================================================================

@router.get("/companies", tags=["Companies"])
async def list_companies(
    vertical: Optional[str] = None,
    stage: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: DatabaseManager = Depends(get_db),
):
    """List all tracked companies."""
    companies = db.list_companies(vertical=vertical, stage=stage, limit=limit)
    return {"companies": [c.to_dict() for c in companies], "count": len(companies)}


@router.get("/companies/{company_id}", tags=["Companies"])
async def get_company(
    company_id: str,
    db: DatabaseManager = Depends(get_db),
):
    """Get a specific company by ID."""
    company = db.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.to_dict()


@router.post("/companies", tags=["Companies"], status_code=201)
async def create_company(
    company: CompanyCreate,
    db: DatabaseManager = Depends(get_db),
):
    """Create a new company."""
    existing = db.get_company(company.id)
    if existing:
        raise HTTPException(status_code=409, detail="Company already exists")

    new_company = db.add_company(company.model_dump())
    if not new_company:
        raise HTTPException(status_code=500, detail="Failed to create company")

    return new_company.to_dict()


@router.put("/companies/{company_id}", tags=["Companies"])
async def update_company(
    company_id: str,
    updates: CompanyUpdate,
    db: DatabaseManager = Depends(get_db),
):
    """Update a company."""
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated = db.update_company(company_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")

    return updated.to_dict()


@router.delete("/companies/{company_id}", tags=["Companies"])
async def delete_company(
    company_id: str,
    db: DatabaseManager = Depends(get_db),
):
    """Delete a company."""
    deleted = db.delete_company(company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")

    return {"message": "Company deleted successfully"}


# =============================================================================
# Deal endpoints
# =============================================================================

@router.get("/deals", tags=["Deals"])
async def list_deals(
    status: Optional[str] = None,
    company_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: DatabaseManager = Depends(get_db),
):
    """List all deals in pipeline."""
    deals = db.list_deals(status=status, company_id=company_id, limit=limit)
    return {"deals": [d.to_dict() for d in deals], "count": len(deals)}


@router.get("/deals/{deal_id}", tags=["Deals"])
async def get_deal(
    deal_id: str,
    db: DatabaseManager = Depends(get_db),
):
    """Get a specific deal by ID."""
    deal = db.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal.to_dict()


@router.post("/deals", tags=["Deals"], status_code=201)
async def create_deal(
    deal: DealCreate,
    db: DatabaseManager = Depends(get_db),
):
    """Create a new deal."""
    new_deal = db.add_deal(deal.model_dump())
    if not new_deal:
        raise HTTPException(status_code=500, detail="Failed to create deal")

    return new_deal.to_dict()


@router.put("/deals/{deal_id}/status", tags=["Deals"])
async def update_deal_status(
    deal_id: str,
    status_update: DealStatusUpdate,
    db: DatabaseManager = Depends(get_db),
):
    """Update a deal's status."""
    updated = db.update_deal_status(deal_id, status_update.status)

    if not updated:
        raise HTTPException(status_code=404, detail="Deal not found")

    return updated.to_dict()


# =============================================================================
# Investment endpoints
# =============================================================================

@router.get("/investments", tags=["Investments"])
async def list_investments(
    status: Optional[str] = None,
    company_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: DatabaseManager = Depends(get_db),
):
    """List all investments."""
    investments = db.list_investments(status=status, company_id=company_id, limit=limit)
    return {"investments": [i.to_dict() for i in investments], "count": len(investments)}


@router.get("/investments/{investment_id}", tags=["Investments"])
async def get_investment(
    investment_id: str,
    db: DatabaseManager = Depends(get_db),
):
    """Get a specific investment by ID."""
    investment = db.get_investment(investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment.to_dict()


@router.post("/investments", tags=["Investments"], status_code=201)
async def create_investment(
    investment: InvestmentCreate,
    db: DatabaseManager = Depends(get_db),
):
    """Record a new investment."""
    new_investment = db.add_investment(investment.model_dump())
    if not new_investment:
        raise HTTPException(status_code=500, detail="Failed to create investment")

    return new_investment.to_dict()


@router.put("/investments/{investment_id}/value", tags=["Investments"])
async def update_investment_value(
    investment_id: str,
    value_update: InvestmentValueUpdate,
    db: DatabaseManager = Depends(get_db),
):
    """Update an investment's current value."""
    updated = db.update_investment_value(investment_id, value_update.current_value_usd)

    if not updated:
        raise HTTPException(status_code=404, detail="Investment not found")

    return updated.to_dict()


# =============================================================================
# Alert endpoints
# =============================================================================

@router.get("/alerts", tags=["Alerts"])
async def list_alerts(
    priority: Optional[str] = None,
    acknowledged: bool = False,
    limit: int = Query(default=100, le=1000),
    db: DatabaseManager = Depends(get_db),
):
    """List alerts."""
    if not acknowledged:
        alerts = db.get_unacknowledged_alerts(priority=priority, limit=limit)
    else:
        # Would need to add method for all alerts
        alerts = db.get_unacknowledged_alerts(priority=priority, limit=limit)

    return {"alerts": [a.to_dict() for a in alerts], "count": len(alerts)}


@router.post("/alerts", tags=["Alerts"], status_code=201)
async def create_alert(
    alert: AlertCreate,
    db: DatabaseManager = Depends(get_db),
):
    """Create a new alert."""
    new_alert = db.add_alert(alert.model_dump())
    if not new_alert:
        raise HTTPException(status_code=500, detail="Failed to create alert")

    return new_alert.to_dict()


@router.put("/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(
    alert_id: str,
    user: str = Query(default="api"),
    db: DatabaseManager = Depends(get_db),
):
    """Acknowledge an alert."""
    acknowledged = db.acknowledge_alert(alert_id, user)

    if not acknowledged:
        raise HTTPException(status_code=404, detail="Alert not found")

    return acknowledged.to_dict()


# =============================================================================
# Research endpoints
# =============================================================================

@router.get("/research/{company_id}", tags=["Research"])
async def get_research(
    company_id: str,
    db: DatabaseManager = Depends(get_db),
):
    """Get latest research for a company."""
    research = db.get_latest_research(company_id)
    if not research:
        raise HTTPException(status_code=404, detail="No research found for company")
    return research.to_dict()


@router.get("/research/{company_id}/history", tags=["Research"])
async def get_research_history(
    company_id: str,
    limit: int = Query(default=10, le=100),
    db: DatabaseManager = Depends(get_db),
):
    """Get research history for a company."""
    history = db.get_research_history(company_id, limit=limit)
    return {"research": [r.to_dict() for r in history], "count": len(history)}


@router.post("/research", tags=["Research"], status_code=201)
async def create_research(
    research: ResearchCreate,
    db: DatabaseManager = Depends(get_db),
):
    """Record new research."""
    new_research = db.add_research(research.model_dump())
    if not new_research:
        raise HTTPException(status_code=500, detail="Failed to create research record")

    return new_research.to_dict()


# =============================================================================
# Portfolio endpoints
# =============================================================================

@router.get("/portfolio/summary", tags=["Portfolio"])
async def get_portfolio_summary(
    db: DatabaseManager = Depends(get_db),
):
    """Get portfolio summary statistics."""
    summary = db.get_portfolio_summary()
    return summary


# =============================================================================
# Health check
# =============================================================================

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }
