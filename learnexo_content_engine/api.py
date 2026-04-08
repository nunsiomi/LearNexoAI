from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.routes.learning_style import router as learning_style_router
from app.routes.learning_path import router as learning_path_router
from app.routes.content import router as content_router
from app.routes.pipeline import router as pipeline_router

app = FastAPI(
    title="LearNexo Content Engine",
    description=(
        "AI-powered content generation service for LearNexo. "
        "Supports learning style detection, personalized curriculum generation, "
        "content generation, full pipeline execution, and optional video recommendations "
        "for Nigerian secondary school students."
    ),
    version="2.0.0",
    contact={"name": "LearNexo AI Team"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"], summary="Health check")
def health_check():
    return {
        "status": "ok",
        "service": "learnexo-content-engine",
    }


# Main API routers
# These will automatically appear in Swagger if their route decorators
# are not hidden with include_in_schema=False.
app.include_router(learning_style_router)   # Stage 1
app.include_router(learning_path_router)    # Stage 2
app.include_router(content_router)          # Stage 3
app.include_router(pipeline_router)         # Full pipeline


@app.post(
    "/videos",
    tags=["YouTube Videos — Visual Learners"],
    summary="Recommend YouTube videos for a topic",
    description=(
        "Searches YouTube for educational videos matching the topic, subject, "
        "and class level. Requires the YOUTUBE_API_KEY environment variable to be set."
    ),
)
def videos_endpoint(request: dict):
    try:
        from youtube_recommender import recommend_videos

        result = recommend_videos(
            topic=request.get("topic"),
            subject=request.get("subject"),
            class_level=request.get("class_level"),
            max_results=request.get("max_results", 5),
        )

        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    except EnvironmentError as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc)},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch video recommendations",
        ) from exc