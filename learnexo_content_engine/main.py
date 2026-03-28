from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import learning_path, content, videos, pipeline

app = FastAPI(
    title="LearNexo Content Engine",
    description=(
        "AI-powered content generation service for LearNexo. "
        "Generates personalised learning paths and lesson content for Nigerian "
        "secondary school students (JSS1–SS3) based on their determined learning style."
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


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "learnexo-content-engine"}


app.include_router(learning_path.router)
app.include_router(content.router)
app.include_router(pipeline.router)
app.include_router(videos.router)
