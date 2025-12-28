from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.models.base import get_db
from app.models import User, Insight
from app.schemas import InsightResponse
from app.ai.insights import InsightsEngine
from app.api.auth import get_current_user


router = APIRouter(prefix="/insights", tags=["Insights"])


def generate_insights_task(db: Session, user_id: int):
    """
    Background task to generate insights
    """
    engine = InsightsEngine(db, user_id)
    insights = engine.generate_all_insights()
    
    # Save to database
    for insight in insights:
        db.add(insight)
    
    db.commit()


@router.post("/generate")
def generate_insights(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger insight generation (async)
    """
    # Clear old insights
    db.query(Insight).filter(Insight.user_id == user.id).delete()
    db.commit()
    
    # Generate new insights in background
    background_tasks.add_task(generate_insights_task, db, user.id)
    
    return {"message": "Insight generation started"}


@router.get("/", response_model=List[InsightResponse])
def get_insights(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all generated insights
    """
    insights = db.query(Insight).filter(
        Insight.user_id == user.id
    ).order_by(Insight.created_at.desc()).all()
    
    return insights
