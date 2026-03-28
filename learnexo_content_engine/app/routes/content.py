import traceback
from fastapi import APIRouter, HTTPException

from models import ContentRequest, ContentResponse
from content_generator import generate_content

router = APIRouter(
    prefix="/content",
    tags=["Stage 3 — Content Generation"],
)


@router.post(
    "",
    response_model=ContentResponse,
    summary="Generate learning content for a single topic",
    description=(
        "Given a topic, subject, class level, and learning style, returns fully tailored "
        "lesson content. Visual learners receive concept maps, diagrams, and YouTube videos. "
        "Auditory learners receive narration scripts, mnemonics, and discussion questions. "
        "Kinesthetic learners receive hands-on activities, experiments, and practical exercises. "
        "All content uses Nigerian contexts (Naira, Lagos, markets, local examples)."
    ),
)
def content_endpoint(request: ContentRequest) -> ContentResponse:
    try:
        return generate_content(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "trace": traceback.format_exc()},
        )
