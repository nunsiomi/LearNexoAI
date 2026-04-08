from fastapi import APIRouter, Depends
from app.schemas.learning_style import (
    LearningStyleRequest,
    LearningStyleResponse,
    LearningStyleEvaluation,
)
from app.services.learning_style_service import LearningStyleService
from app.core.dependencies import get_learning_style_service

router = APIRouter(prefix="/api/learning-style", tags=["Learning Style"])

@router.post("/", response_model=LearningStyleResponse)
def detect_learning_style(
    payload: LearningStyleRequest,
    service: LearningStyleService = Depends(get_learning_style_service),
):
    result: LearningStyleEvaluation = service.evaluate(payload.student_activity)
    return LearningStyleResponse(learning_style=result.learning_style)

@router.post("/detailed", response_model=LearningStyleEvaluation)
def detect_learning_style_detailed(
    payload: LearningStyleRequest,
    service: LearningStyleService = Depends(get_learning_style_service),
):
    return service.evaluate(payload.student_activity)