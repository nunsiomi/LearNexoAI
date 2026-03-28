# LearNexo Content Engine

AI-powered microservice that generates personalised learning content for Nigerian secondary school students (JSS1–SS3). It takes a student's pre-determined learning style and produces curriculum-aligned learning paths and full lesson content tailored to how that student learns best.

---

## System Architecture — The 3 Stages

```
┌─────────────────────┐     ┌───────────────────────┐     ┌──────────────────────────┐
│   STAGE 1           │     │   STAGE 2             │     │   STAGE 3                │
│   assessment.py     │────▶│   POST /learning-path │────▶│   POST /content          │
│                     │     │                       │     │                          │
│  Student activity   │     │  Ordered topic list   │     │  Full lesson content     │
│  data in            │     │  per term, aligned    │     │  tailored to the         │
│                     │     │  to WAEC/NECO/JAMB    │     │  student's learning      │
│  Learning style out │     │  with exam tips       │     │  style                   │
│  (visual /          │     │                       │     │                          │
│   auditory /        │     │                       │     │  + YouTube videos for    │
│   kinesthetic)      │     │                       │     │  visual learners         │
└─────────────────────┘     └───────────────────────┘     └──────────────────────────┘
                                        │
                            ┌───────────▼───────────┐
                            │  POST /full-pipeline  │
                            │  Stages 2 + 3 in one  │
                            │  call (onboarding)    │
                            └───────────────────────┘
```

**Stage 1** lives in `assessment.py` — run it standalone to identify a student's learning style from their activity data. Its output (`visual`, `auditory`, or `kinesthetic`) feeds into Stages 2 and 3.

**Stage 2** (`POST /learning-path`) takes the learning style and generates a full term-by-term topic sequence aligned to the Nigerian curriculum with WAEC/NECO/JAMB exam tips.

**Stage 3** (`POST /content`) takes any topic from Stage 2 and generates complete lesson content formatted specifically for the student's learning style.

---

## Content by Learning Style

### Visual Learners
- Concept map / mind map description
- Diagram and illustration descriptions
- Infographic outline
- Colour-coded summary
- Step-by-step visual guide
- Nigerian visual examples (Lagos market, Naira calculations, etc.)
- **YouTube video recommendations** — automatically fetched from the YouTube Data API v3, ranked by educational quality, Nigerian/African channels prioritised

### Auditory Learners
- Full audio narration script (ready for text-to-speech or recording)
- Nigerian storytelling narrative that embeds the concept
- Mnemonics, rhymes, and memory aids
- Discussion questions for class or group oral sessions
- Podcast-style Q&A pairs
- Key points written as they would be spoken aloud

### Kinesthetic Learners
- Hands-on activities (doable at home or in class)
- Simple experiments using everyday Nigerian household items
- Step-by-step practical guide
- Real-world applications in Nigerian daily life contexts
- Interactive exercises with expected outcomes
- Group/collaborative activities

All content uses Nigerian contexts throughout — prices in Naira, locations in Lagos/Abuja/Kano, local food, markets, and everyday Nigerian life.

---

## API Endpoints

### `POST /learning-path` — Stage 2
Generate a personalised learning path for a student.

**Request:**
```json
{
  "learning_style": "visual",
  "subject": "Mathematics",
  "class_level": "SS2",
  "student_id": "stu_001",
  "term": "First"
}
```

**Fields:**
| Field | Type | Required | Options |
|---|---|---|---|
| `learning_style` | string | Yes | `visual`, `auditory`, `kinesthetic` |
| `subject` | string | Yes | See supported subjects below |
| `class_level` | string | Yes | `JSS1`, `JSS2`, `JSS3`, `SS1`, `SS2`, `SS3` |
| `student_id` | string | No | Any identifier string |
| `term` | string | No | `First`, `Second`, `Third` (default: `First`) |

**Response includes:**
- Ordered list of topics with subtopics and learning objectives
- Estimated duration per topic (in hours)
- Content format recommended for this student's style
- Prerequisite topics
- Exam relevance (WAEC/NECO/JAMB)
- Overall study strategy for the style
- WAEC/NECO/JAMB exam tips for the subject

---

### `POST /content` — Stage 3
Generate full lesson content for one topic.

**Request:**
```json
{
  "learning_style": "visual",
  "topic": "Quadratic Equations",
  "subject": "Mathematics",
  "class_level": "SS2",
  "content_depth": "core",
  "student_id": "stu_001"
}
```

**Fields:**
| Field | Type | Required | Options |
|---|---|---|---|
| `learning_style` | string | Yes | `visual`, `auditory`, `kinesthetic` |
| `topic` | string | Yes | Any topic string |
| `subject` | string | Yes | See supported subjects below |
| `class_level` | string | Yes | `JSS1`–`SS3` |
| `content_depth` | string | No | `introduction`, `core`, `advanced`, `revision` (default: `core`) |
| `student_id` | string | No | Any identifier string |

**Response includes:**
- Learning objectives and key concepts
- Style-specific content block (`visual_content`, `auditory_content`, or `kinesthetic_content`)
- For visual learners: YouTube videos automatically attached (see YouTube section below)
- Assessment questions (multiple choice, short answer, theory — WAEC/NECO/JAMB style)
- Key points summary
- Next topic preview
- Study tips for the student's learning style

---

### `POST /videos` — YouTube Video Recommendations
Fetch ranked YouTube videos for any topic. This is the same logic auto-attached to visual learner content responses.

**Request:**
```json
{
  "topic": "Photosynthesis",
  "subject": "Biology",
  "class_level": "SS1",
  "max_results": 5
}
```

**Response includes per video:**
- `title`, `channel_name`, `url`, `thumbnail_url`
- `duration_readable` (e.g. `12 min 30 sec`)
- `view_count`
- `relevance_score` (calculated ranking score)
- `why_recommended` (reason for inclusion)
- `fallback_used` — whether the search fell back to global channels

> **Requires `YOUTUBE_API_KEY`** — see Environment Variables below. If the key is not set, the `/videos` endpoint returns a `503` error, and the `youtube_videos` field in `/content` responses will be `null` rather than blocking the request.

---

### `POST /full-pipeline` — Stages 2 + 3 Combined
Run the full onboarding flow in one call.

**Request:**
```json
{
  "learning_style": "kinesthetic",
  "subject": "Chemistry",
  "class_level": "SS3",
  "student_id": "stu_002",
  "term": "Second",
  "generate_content_for_first_topic": true
}
```

**Response includes:**
- Full learning path (same as `/learning-path`)
- Optionally, full lesson content for the first topic (same as `/content`)

Set `generate_content_for_first_topic: false` if you only need the topic list without the first lesson.

---

### `GET /health` — Health Check
```json
{ "status": "ok", "service": "learnexo-content-engine" }
```

---

## Supported Subjects

Mathematics, English Language, Biology, Chemistry, Physics, Further Mathematics, Economics, Government, Commerce, Agricultural Science, Geography, History, Literature in English, Civic Education, Computer Science, Basic Technology, Home Economics, French, Yoruba, Igbo, Hausa.

---

## Environment Variables

Create a `.env` file by copying `.env.example`:

```bash
cp .env.example .env
```

| Variable | Required | Purpose | Where to get it |
|---|---|---|---|
| `GROQ_API_KEY` | **Required** | Powers all AI content generation (LLM calls) | [console.groq.com](https://console.groq.com) — free tier available |
| `YOUTUBE_API_KEY` | **Required for `/videos`** | Fetches and ranks YouTube educational videos | [console.cloud.google.com](https://console.cloud.google.com) → Enable "YouTube Data API v3" → Credentials |

**Important:**
- Never commit your `.env` file. It is blocked by `.gitignore`.
- If `YOUTUBE_API_KEY` is missing, the `/videos` endpoint returns `503` and visual learner responses return `youtube_videos: null` — all other content still generates normally.
- If `GROQ_API_KEY` is missing, all AI endpoints return `500`.

---

## Running Locally

**Prerequisites:** Python 3.11+

```bash
# 1. Clone the repo and enter the folder
cd learnexo_content_engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and YOUTUBE_API_KEY

# 4. Start the server
uvicorn main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.
Interactive Swagger docs: `http://localhost:8000/docs`

---

## File Structure

```
learnexo_content_engine/
├── main.py                        # FastAPI app entry point — registers all routes
├── assessment.py                  # Stage 1 — learning style detector (standalone script)
│
├── app/
│   └── routes/
│       ├── learning_path.py       # POST /learning-path (Stage 2)
│       ├── content.py             # POST /content (Stage 3)
│       ├── pipeline.py            # POST /full-pipeline (Stages 2+3)
│       └── videos.py              # POST /videos (YouTube recommendations)
│
├── models.py                      # All Pydantic request/response models
├── prompts.py                     # LangChain prompt templates per learning style
├── llm_config.py                  # Groq LLM setup (llama-3.3-70b-versatile)
├── learning_path_generator.py     # Stage 2 business logic
├── content_generator.py           # Stage 3 business logic + YouTube attachment
├── youtube_recommender.py         # YouTube Data API v3 search, filter, and ranking
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Template — copy to .env and fill in keys
└── .gitignore                     # Blocks .env, __pycache__, *.pyc
```

---

## Backend Integration Guide

This service is designed to run as a **standalone microservice** alongside your main backend. Your backend calls it over HTTP — no shared codebase or imports required.

### Step 1 — Run the content engine
Deploy or run `uvicorn main:app --host 0.0.0.0 --port 8000` and note the base URL (e.g. `http://content-engine:8000`).

### Step 2 — Student onboarding flow
When a new student completes the learning style assessment (Stage 1), call `/full-pipeline` with the result:

```python
import httpx

CONTENT_ENGINE_URL = "http://content-engine:8000"

async def onboard_student(student_id: str, learning_style: str, subject: str, class_level: str):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{CONTENT_ENGINE_URL}/full-pipeline",
            json={
                "learning_style": learning_style,   # from Stage 1 assessment
                "subject": subject,
                "class_level": class_level,
                "student_id": student_id,
                "term": "First",
                "generate_content_for_first_topic": True,
            }
        )
        return response.json()
        # Returns: learning_path (full topic list) + first_topic_content (first lesson)
```

### Step 3 — Fetching content for subsequent topics
When the student moves to the next topic, call `/content`:

```python
async def get_topic_content(student_id: str, learning_style: str, topic: str, subject: str, class_level: str):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{CONTENT_ENGINE_URL}/content",
            json={
                "learning_style": learning_style,
                "topic": topic,
                "subject": subject,
                "class_level": class_level,
                "content_depth": "core",
                "student_id": student_id,
            }
        )
        return response.json()
```

### Step 4 — Consuming the content response
The response always includes the same top-level structure. Only one of the three content blocks will be populated, depending on the student's learning style:

```python
content = response.json()

# Always present
objectives    = content["learning_objectives"]
key_concepts  = content["key_concepts"]
assessment    = content["assessment_questions"]
summary       = content["key_points_summary"]
study_tips    = content["study_tips_for_style"]
next_topic    = content["next_topic_preview"]

# Only one of these will be non-null
if content["visual_content"]:
    concept_map   = content["visual_content"]["concept_map"]
    diagrams      = content["visual_content"]["diagram_descriptions"]
    youtube_videos = content["visual_content"]["youtube_videos"]  # list or null
    # youtube_videos[i] has: title, channel_name, url, thumbnail_url, duration_readable, view_count, why_recommended

elif content["auditory_content"]:
    script        = content["auditory_content"]["audio_narration_script"]
    mnemonics     = content["auditory_content"]["mnemonics_and_songs"]
    story         = content["auditory_content"]["storytelling_narrative"]

elif content["kinesthetic_content"]:
    activities    = content["kinesthetic_content"]["hands_on_activities"]
    experiment    = content["kinesthetic_content"]["experiment_or_simulation"]
    group_task    = content["kinesthetic_content"]["group_activity"]
```

### Step 5 — Standalone YouTube recommendations
To fetch videos independently (e.g. for a "watch more" feature):

```python
async def get_videos(topic: str, subject: str, class_level: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{CONTENT_ENGINE_URL}/videos",
            json={"topic": topic, "subject": subject, "class_level": class_level, "max_results": 5}
        )
        if response.status_code == 503:
            return []  # YouTube API key not configured
        return response.json()["videos"]
```

### Error handling
| Status | Meaning |
|---|---|
| `200` | Success |
| `422` | Invalid request body (check field names and allowed values) |
| `500` | AI generation failed (check `GROQ_API_KEY` and Groq service status) |
| `503` | YouTube API unavailable (check `YOUTUBE_API_KEY`) |

---

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| AI Model | Groq — `llama-3.3-70b-versatile` |
| AI Orchestration | LangChain + LangChain-Groq |
| Data Validation | Pydantic v2 |
| YouTube Integration | YouTube Data API v3 (via `google-api-python-client`) |
| Environment Config | python-dotenv |
| Language | Python 3.11+ |

---

## Curriculum Alignment

All content is aligned to the **Nigerian secondary school curriculum**:
- **WAEC** (West African Examinations Council)
- **NECO** (National Examinations Council)
- **JAMB** (Joint Admissions and Matriculation Board)

Every learning path includes subject-specific exam tips, topic-level exam relevance notes, and assessment questions that mirror WAEC/NECO/JAMB question formats.
