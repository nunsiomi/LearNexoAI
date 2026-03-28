import traceback
from fastapi import APIRouter, HTTPException

from models import LearningPathRequest, LearningPathResponse
from learning_path_generator import generate_learning_path

router = APIRouter(
    prefix="/learning-path",
    tags=["Stage 2 — Learning Path"],
)


@router.post(
    "",
    response_model=LearningPathResponse,
    summary="Generate a personalised learning path",
    description=(
        "Given a student's learning style, subject, and class level, returns a full "
        "Nigerian-curriculum-aligned learning path with topics, estimated durations, "
        "content formats adapted to the student's style, and WAEC/NECO/JAMB exam tips."
    ),
)
def learning_path_endpoint(request: LearningPathRequest) -> LearningPathResponse:
    try:
        return generate_learning_path(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "trace": traceback.format_exc()},
        )
