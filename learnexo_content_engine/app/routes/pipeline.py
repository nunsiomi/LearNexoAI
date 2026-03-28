import traceback
from fastapi import APIRouter, HTTPException

from models import (
    LearningPathRequest,
    ContentRequest,
    FullPipelineRequest,
    FullPipelineResponse,
)
from learning_path_generator import generate_learning_path
from content_generator import generate_content

router = APIRouter(
    prefix="/full-pipeline",
    tags=["Full Pipeline"],
)


@router.post(
    "",
    response_model=FullPipelineResponse,
    summary="Run Stages 2 + 3 together",
    description=(
        "Convenience endpoint that runs the learning path generator and — optionally — "
        "also generates full lesson content for the first topic in the path. "
        "Use this for student onboarding where you need both a roadmap and immediate lesson content."
    ),
)
def full_pipeline_endpoint(request: FullPipelineRequest) -> FullPipelineResponse:
    try:
        path_request = LearningPathRequest(
            learning_style=request.learning_style,
            subject=request.subject,
            class_level=request.class_level,
            student_id=request.student_id,
            term=request.term,
        )
        learning_path = generate_learning_path(path_request)

        first_topic_content = None
        if request.generate_content_for_first_topic and learning_path.topics:
            first_topic = learning_path.topics[0]
            content_request = ContentRequest(
                learning_style=request.learning_style,
                topic=first_topic.topic,
                subject=request.subject,
                class_level=request.class_level,
                content_depth="introduction",
                student_id=request.student_id,
            )
            first_topic_content = generate_content(content_request)

        return FullPipelineResponse(
            learning_path=learning_path,
            first_topic_content=first_topic_content,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "trace": traceback.format_exc()},
        )
