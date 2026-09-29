from fastapi import APIRouter
from app.models.schemas import TelemetryDashboardResponse
from app.services.telemetry_service import telemetry_service

router = APIRouter(prefix="/telemetry", tags=["Government Oversight & Telemetry"])


@router.get("/dashboard", response_model=TelemetryDashboardResponse)
def get_telemetry_metrics():
    """
    Returns live system analytics for Government Oversight & System Administrators:
    - User query volume & persona breakdown
    - Feedback satisfaction rate
    - Total standards & extracted tables indexed
    - Compliance audit pass/fail ratios
    - Recent logs
    """
    return telemetry_service.get_dashboard_metrics()
