from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

from app.services.content_service import ContentService

router = APIRouter(
    prefix="/content",
    tags=["Stage 3 — Content Generation"],
)

LearningStyle = Literal["visual", "auditory", "kinesthetic"]
ClassLevel = Literal["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]


class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="Topic to generate content for")
    subject: str = Field(..., min_length=2, description="School subject")
    class_level: ClassLevel = Field(..., description="Student class level")
    learning_style: LearningStyle = Field(
        ...,
        description="Student learning style",
    )
    generated_curriculum: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional curriculum output from Stage 2",
    )
    student_id: Optional[str] = Field(
        default=None,
        description="Optional student identifier",
    )
    content_depth: str = Field(
        default="core",
        description="Depth of generated content, e.g. core, standard, detailed",
    )


class ContentResponse(BaseModel):
    topic: str
    subject: str
    class_level: ClassLevel
    learning_style: LearningStyle
    content: dict[str, Any]


def get_content_service() -> ContentService:
    return ContentService()


@router.post(
    "",
    response_model=ContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate learning content for a single topic",
    description=(
        "Given a topic, subject, class level, and learning style, returns fully tailored "
        "lesson content. Visual learners receive diagrams, structured notes, and concept maps. "
        "Auditory learners receive explanations, spoken-style summaries, and discussion prompts. "
        "Kinesthetic learners receive hands-on tasks, exercises, and practical activities."
    ),
)
@router.post(
    "/",
    response_model=ContentResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def content_endpoint(
    request: ContentRequest,
    service: ContentService = Depends(get_content_service),
) -> ContentResponse:
    try:
        result = service.generate(
            topic=request.topic,
            subject=request.subject,
            class_level=request.class_level,
            learning_style=request.learning_style,
            generated_curriculum=request.generated_curriculum,
            student_id=request.student_id,
            content_depth=request.content_depth,
        )

        return ContentResponse(
            topic=request.topic,
            subject=request.subject,
            class_level=request.class_level,
            learning_style=request.learning_style,
            content=result,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate content",
        ) from exc