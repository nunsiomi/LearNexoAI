from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

from app.services.learning_path_service import LearningPathService

router = APIRouter(prefix="/learning-path", tags=["Learning Path"])

LearningStyle = Literal["visual", "auditory", "kinesthetic"]
ClassLevel = Literal["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]
TermName = Literal["First", "Second", "Third"]


class LearningPathRequest(BaseModel):
    learning_style: LearningStyle = Field(
        ...,
        description="Student learning style: visual, auditory, or kinesthetic",
    )
    subject: str = Field(
        ...,
        min_length=2,
        description="School subject, e.g. Mathematics, English, Biology",
    )
    class_level: ClassLevel = Field(
        ...,
        description="Student class level",
    )
    student_id: Optional[str] = Field(
        default=None,
        description="Optional student identifier",
    )
    term: TermName = Field(
        default="First",
        description="Academic term",
    )


class LearningPathResponse(BaseModel):
    learning_style: LearningStyle
    subject: str
    class_level: ClassLevel
    term: TermName
    student_id: Optional[str] = None
    learning_path: dict[str, Any]


def get_learning_path_service() -> LearningPathService:
    return LearningPathService()


@router.post(
    "",
    response_model=LearningPathResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate personalized learning path",
)
@router.post(
    "/",
    response_model=LearningPathResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def generate_learning_path(
    payload: LearningPathRequest,
    service: LearningPathService = Depends(get_learning_path_service),
) -> LearningPathResponse:
    try:
        result = service.generate(
            learning_style=payload.learning_style,
            subject=payload.subject,
            class_level=payload.class_level,
            student_id=payload.student_id,
            term=payload.term,
        )

        return LearningPathResponse(
            learning_style=payload.learning_style,
            subject=payload.subject,
            class_level=payload.class_level,
            term=payload.term,
            student_id=payload.student_id,
            learning_path=result,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning path",
        ) from exc