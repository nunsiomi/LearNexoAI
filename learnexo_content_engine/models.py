from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field


# ─── Shared Enums / Literals ────────────────────────────────────────────────

LearningStyle = Literal["visual", "auditory", "kinesthetic"]

ClassLevel = Literal["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]

Subject = Literal[
    "Mathematics",
    "English Language",
    "Biology",
    "Chemistry",
    "Physics",
    "Further Mathematics",
    "Economics",
    "Government",
    "Commerce",
    "Agricultural Science",
    "Geography",
    "History",
    "Literature in English",
    "Civic Education",
    "Computer Science",
    "Basic Technology",
    "Home Economics",
    "French",
    "Yoruba",
    "Igbo",
    "Hausa",
]

ContentDepth = Literal["introduction", "core", "advanced", "revision"]


# ─── Stage 2: Learning Path Models ──────────────────────────────────────────

class LearningPathRequest(BaseModel):
    learning_style: LearningStyle = Field(
        ..., description="Student's determined learning style"
    )
    subject: str = Field(
        ..., description="Nigerian curriculum subject (e.g. Mathematics, Biology)"
    )
    class_level: ClassLevel = Field(
        ..., description="Student's class level (e.g. SS2, JSS3)"
    )
    student_id: Optional[str] = Field(
        None, description="Optional student identifier for tracking"
    )
    term: Optional[Literal["First", "Second", "Third"]] = Field(
        "First", description="Nigerian academic term"
    )


class TopicNode(BaseModel):
    order: int = Field(..., description="Position in learning sequence (1-based)")
    topic: str = Field(..., description="Topic name aligned with Nigerian curriculum")
    subtopics: List[str] = Field(..., description="Key subtopics to cover")
    learning_objectives: List[str] = Field(
        ..., description="What the student will be able to do after this topic"
    )
    estimated_duration_hours: float = Field(
        ..., description="Estimated study time in hours"
    )
    content_format: str = Field(
        ...,
        description="Primary content format recommended for this student's learning style",
    )
    prerequisite_topics: List[str] = Field(
        default_factory=list,
        description="Topics the student should complete before this one",
    )
    exam_relevance: str = Field(
        ...,
        description="How this topic relates to WAEC/NECO/JAMB examinations",
    )


class LearningPathResponse(BaseModel):
    student_id: Optional[str]
    learning_style: LearningStyle
    subject: str
    class_level: ClassLevel
    term: str
    total_topics: int
    total_estimated_hours: float
    style_strategy: str = Field(
        ...,
        description="Overall explanation of how content is adapted to this learning style",
    )
    topics: List[TopicNode]
    exam_tips: List[str] = Field(
        ..., description="WAEC/NECO/JAMB specific tips for this subject and style"
    )


# ─── Stage 3: Content Generation Models ─────────────────────────────────────

class ContentRequest(BaseModel):
    learning_style: LearningStyle
    topic: str = Field(..., description="Topic to generate content for")
    subject: str = Field(..., description="Subject the topic belongs to")
    class_level: ClassLevel
    content_depth: ContentDepth = Field(
        "core", description="Depth level of the content to generate"
    )
    student_id: Optional[str] = None


class VisualContent(BaseModel):
    concept_map: str = Field(
        ...,
        description="Text description of a concept map/mind map for this topic",
    )
    diagram_descriptions: List[str] = Field(
        ...,
        description="Detailed descriptions of diagrams/illustrations to display",
    )
    step_by_step_visual_guide: List[str] = Field(
        ..., description="Numbered visual steps or processes"
    )
    color_coded_summary: str = Field(
        ...,
        description="Summary using colour-coded categories (described in text for rendering)",
    )
    infographic_outline: str = Field(
        ..., description="Structure for a key-facts infographic"
    )
    nigerian_visual_examples: List[str] = Field(
        ...,
        description="Examples using familiar Nigerian contexts (markets, cities, everyday life)",
    )
    youtube_videos: Optional[List[Any]] = Field(
        None,
        description="Recommended YouTube videos fetched from the YouTube Data API v3. "
                    "Each item is a YouTubeVideo object. Only present for visual learners "
                    "when the YouTube API key is configured.",
    )


class AuditoryContent(BaseModel):
    audio_narration_script: str = Field(
        ...,
        description="Full spoken-word script for an audio lesson on this topic",
    )
    discussion_questions: List[str] = Field(
        ...,
        description="Discussion questions for group or class oral discussion",
    )
    mnemonics_and_songs: List[str] = Field(
        ..., description="Memory aids, rhymes, or mnemonic devices"
    )
    storytelling_narrative: str = Field(
        ...,
        description="A short story or narrative that embeds the concept using a Nigerian setting",
    )
    verbal_summary_bullets: List[str] = Field(
        ..., description="Key points written as they would be spoken aloud"
    )
    podcast_style_q_and_a: List[dict] = Field(
        ...,
        description="List of question/answer pairs suitable for an audio Q&A format",
    )


class KinestheticContent(BaseModel):
    hands_on_activities: List[str] = Field(
        ...,
        description="Practical activities students can physically do to learn the concept",
    )
    real_world_applications: List[str] = Field(
        ...,
        description="Real-world scenarios (relevant to Nigerian daily life) where this concept applies",
    )
    step_by_step_practice_guide: List[str] = Field(
        ..., description="A detailed guide for working through a practical task"
    )
    interactive_exercises: List[dict] = Field(
        ...,
        description="Structured exercises with clear instructions and expected outcomes",
    )
    experiment_or_simulation: str = Field(
        ...,
        description="A simple experiment or simulation activity (can be done with everyday items)",
    )
    group_activity: str = Field(
        ..., description="A collaborative group activity that reinforces learning through doing"
    )


class AssessmentQuestion(BaseModel):
    question_type: Literal["multiple_choice", "short_answer", "theory"]
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    exam_source: Optional[str] = Field(
        None,
        description="If this mirrors a WAEC/NECO/JAMB style question, note it here",
    )


class ContentResponse(BaseModel):
    student_id: Optional[str]
    learning_style: LearningStyle
    subject: str
    class_level: ClassLevel
    topic: str
    content_depth: ContentDepth
    learning_objectives: List[str]
    key_concepts: List[str]
    visual_content: Optional[VisualContent] = None
    auditory_content: Optional[AuditoryContent] = None
    kinesthetic_content: Optional[KinestheticContent] = None
    assessment_questions: List[AssessmentQuestion]
    key_points_summary: List[str]
    next_topic_preview: str
    study_tips_for_style: List[str] = Field(
        ...,
        description="Specific study tips tailored to this student's learning style",
    )


# ─── YouTube Video Recommendation Request ────────────────────────────────────

class VideoRecommendRequest(BaseModel):
    topic: str = Field(..., description="Topic to find YouTube videos for")
    subject: str = Field(..., description="Subject (e.g. Biology, Mathematics)")
    class_level: ClassLevel = Field(..., description="Student's class level (e.g. SS1, SS2)")
    max_results: int = Field(
        5, ge=1, le=10, description="Number of videos to return (1–10)"
    )


# ─── Full Pipeline Model ─────────────────────────────────────────────────────

class FullPipelineRequest(BaseModel):
    learning_style: LearningStyle
    subject: str
    class_level: ClassLevel
    student_id: Optional[str] = None
    term: Optional[Literal["First", "Second", "Third"]] = "First"
    generate_content_for_first_topic: bool = Field(
        True,
        description="Whether to also generate full content for the first topic in the path",
    )


class FullPipelineResponse(BaseModel):
    learning_path: LearningPathResponse
    first_topic_content: Optional[ContentResponse] = None
