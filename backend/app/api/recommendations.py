from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ...models.base import get_db
from ...models import User
from ...schemas import RecommendationResponse
from ...ai.recommendations import RecommendationEngine
from .auth import get_current_user

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
