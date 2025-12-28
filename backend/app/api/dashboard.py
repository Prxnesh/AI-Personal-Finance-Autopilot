from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models import User
from app.schemas import DashboardResponse
from app.services.dashboard_service import get_dashboard_data
from app.api.auth import get_current_user


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data
    """
    return get_dashboard_data(db, user.id)
