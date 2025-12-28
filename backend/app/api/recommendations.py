from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.base import get_db
from app.models import User
from app.schemas import RecommendationResponse
from app.ai.recommendations import RecommendationEngine
from app.api.auth import get_current_user


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated financial recommendations
    """
    engine = RecommendationEngine(db, user.id)
    recommendations = engine.generate_recommendations()
    
    return recommendations
