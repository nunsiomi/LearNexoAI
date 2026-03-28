"""
LearNexo Content Engine — FastAPI Service

Provides four endpoints for the backend engineer to integrate:

  POST /learning-path  → Stage 2: Generate a learning path
  POST /content        → Stage 3: Generate content for a single topic
  POST /full-pipeline  → Stages 2+3: Learning path + first-topic content in one call
  POST /videos         → YouTube video recommendations for visual learners

Run locally:
  uvicorn api:app --reload --port 8000

Or via the workflow:
  python -m uvicorn api:app --host 0.0.0.0 --port $PORT
"""

import json
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    LearningPathRequest,
    LearningPathResponse,
    ContentRequest,
    VideoRecommendRequest,
    ContentResponse,
    FullPipelineRequest,
    FullPipelineResponse,
)
from learning_path_generator import generate_learning_path
from content_generator import generate_content

app = FastAPI(
    title="LearNexo Content Engine",
    description=(
        "AI-powered content generation service for LearNexo. "
        "Generates personalized learning paths and lesson content for Nigerian "
        "secondary school students based on their determined learning style."
    ),
    version="1.0.0",
    contact={"name": "LearNexo AI Team"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Check that the content engine is running."""
    return {"status": "ok", "service": "learnexo-content-engine"}


# ─── Stage 2: Learning Path ───────────────────────────────────────────────────

@app.post(
    "/learning-path",
    response_model=LearningPathResponse,
    tags=["Stage 2 — Learning Path"],
    summary="Generate a personalized learning path",
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


# ─── Stage 3: Content Generation ─────────────────────────────────────────────

@app.post(
    "/content",
    response_model=ContentResponse,
    tags=["Stage 3 — Content Generation"],
    summary="Generate learning content for a single topic",
    description=(
        "Given a topic, subject, class level, and learning style, returns fully tailored "
        "lesson content. Visual learners receive concept maps, diagrams, and infographics. "
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


# ─── Full Pipeline ────────────────────────────────────────────────────────────

@app.post(
    "/full-pipeline",
    response_model=FullPipelineResponse,
    tags=["Full Pipeline"],
    summary="Run Stages 2+3 together",
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


# ─── YouTube Video Recommendations ───────────────────────────────────────────

@app.post(
    "/videos",
    tags=["YouTube Videos — Visual Learners"],
    summary="Recommend YouTube videos for a topic",
    description=(
        "Searches YouTube for educational videos matching the topic, subject, and class level. "
        "Results are filtered for educational relevance and ranked — Nigerian/African channels "
        "are prioritised, then globally trusted channels (Khan Academy, CrashCourse, TED-Ed, etc.). "
        "Each video includes title, channel, URL, thumbnail, duration, view count, and a short "
        "explanation of why it was recommended. "
        "Requires the YOUTUBE_API_KEY environment variable to be set."
    ),
)
def videos_endpoint(request: VideoRecommendRequest):
    try:
        from youtube_recommender import recommend_videos
        result = recommend_videos(
            topic=request.topic,
            subject=request.subject,
            class_level=request.class_level,
            max_results=request.max_results,
        )
        return result.model_dump()
    except EnvironmentError as e:
        raise HTTPException(
            status_code=503,
            detail={"error": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "trace": traceback.format_exc()},
        )
