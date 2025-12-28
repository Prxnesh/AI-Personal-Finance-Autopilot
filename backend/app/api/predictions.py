from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.models.base import get_db
from app.models import User, Prediction
from app.schemas import PredictionResponse
from app.ai.predictions import PredictionEngine
from app.api.auth import get_current_user


router = APIRouter(prefix="/predictions", tags=["Predictions"])


def generate_predictions_task(db: Session, user_id: int):
    """
    Background task to generate predictions
    """
    engine = PredictionEngine(db, user_id)
    predictions = engine.generate_predictions()
    
    # Save to database
    for prediction in predictions:
        db.add(prediction)
    
    db.commit()


@router.post("/generate")
def generate_predictions(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger prediction generation (async)
    """
    # Clear old predictions
    db.query(Prediction).filter(Prediction.user_id == user.id).delete()
    db.commit()
    
    # Generate new predictions in background
    background_tasks.add_task(generate_predictions_task, db, user.id)
    
    return {"message": "Prediction generation started"}


@router.get("/", response_model=List[PredictionResponse])
def get_predictions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all generated predictions
    """
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user.id
    ).order_by(Prediction.created_at.desc()).all()
    
    return predictions
