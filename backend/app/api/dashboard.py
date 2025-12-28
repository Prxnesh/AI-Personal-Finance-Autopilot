from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...models.base import get_db
from ...models import User
from ...schemas import DashboardResponse
from ...services.dashboard_service import get_dashboard_data
from .auth import get_current_user

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
