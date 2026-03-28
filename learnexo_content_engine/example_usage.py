"""
LearNexo Content Engine — Example Usage

Demonstrates how to use the content engine directly in Python
(without going through the FastAPI server).

Run:
  python example_usage.py

Make sure GROQ_API_KEY is set in your .env file first.
"""

import json
from models import LearningPathRequest, ContentRequest, FullPipelineRequest
from learning_path_generator import generate_learning_path
from content_generator import generate_content


def demo_learning_path():
    """Stage 2 demo: Generate a learning path for a visual learner in SS2 Mathematics."""

    print("\n" + "=" * 60)
    print("STAGE 2 — LEARNING PATH GENERATOR")
    print("=" * 60)

    request = LearningPathRequest(
        learning_style="visual",
        subject="Mathematics",
        class_level="SS2",
        term="First",
        student_id="stu_001",
    )

    print(f"\nGenerating learning path for:")
    print(f"  Learning Style : {request.learning_style}")
    print(f"  Subject        : {request.subject}")
    print(f"  Class Level    : {request.class_level}")
    print(f"  Term           : {request.term}")
    print("\nPlease wait — calling LLM...\n")

    path = generate_learning_path(request)

    print(f"✓ Generated {path.total_topics} topics ({path.total_estimated_hours:.1f} hrs total)\n")
    print(f"Style Strategy:\n  {path.style_strategy}\n")

    print("Topics:")
    for t in path.topics:
        print(f"  {t.order}. {t.topic}")
        print(f"     Format    : {t.content_format}")
        print(f"     Duration  : {t.estimated_duration_hours}h")
        print(f"     WAEC Note : {t.exam_relevance}")
        print()

    print("Exam Tips:")
    for tip in path.exam_tips:
        print(f"  • {tip}")

    return path


def demo_visual_content():
    """Stage 3 demo: Generate visual content for Quadratic Equations."""

    print("\n" + "=" * 60)
    print("STAGE 3 — CONTENT GENERATOR (VISUAL LEARNER)")
    print("=" * 60)

    request = ContentRequest(
        learning_style="visual",
        topic="Quadratic Equations",
        subject="Mathematics",
        class_level="SS2",
        content_depth="core",
        student_id="stu_001",
    )

    print(f"\nGenerating visual content for: {request.topic}")
    print("Please wait — calling LLM...\n")

    content = generate_content(request)

    print(f"Topic          : {content.topic}")
    print(f"Learning Style : {content.learning_style}")
    print(f"Subject        : {content.subject} ({content.class_level})\n")

    print("Learning Objectives:")
    for obj in content.learning_objectives:
        print(f"  • {obj}")

    print("\nKey Concepts:")
    for kc in content.key_concepts:
        print(f"  • {kc}")

    if content.visual_content:
        vc = content.visual_content
        print("\nConcept Map (description):")
        print(f"  {vc.concept_map}")
        print("\nDiagram Descriptions:")
        for d in vc.diagram_descriptions:
            print(f"  → {d}")
        print("\nNigerian Examples:")
        for ex in vc.nigerian_visual_examples:
            print(f"  → {ex}")
        print("\nColor-Coded Summary:")
        print(f"  {vc.color_coded_summary}")

    print("\nAssessment Questions:")
    for i, q in enumerate(content.assessment_questions, 1):
        print(f"\n  Q{i} [{q.question_type}]: {q.question}")
        if q.options:
            for opt in q.options:
                print(f"    {opt}")
        print(f"  Answer: {q.correct_answer}")
        print(f"  Explanation: {q.explanation}")

    print("\nKey Points Summary:")
    for pt in content.key_points_summary:
        print(f"  • {pt}")

    print(f"\nNext Topic Preview: {content.next_topic_preview}")

    print("\nStudy Tips for Visual Learners:")
    for tip in content.study_tips_for_style:
        print(f"  • {tip}")

    return content


def demo_auditory_content():
    """Stage 3 demo: Generate auditory content for Photosynthesis."""

    print("\n" + "=" * 60)
    print("STAGE 3 — CONTENT GENERATOR (AUDITORY LEARNER)")
    print("=" * 60)

    request = ContentRequest(
        learning_style="auditory",
        topic="Photosynthesis",
        subject="Biology",
        class_level="SS1",
        content_depth="core",
        student_id="stu_002",
    )

    print(f"\nGenerating auditory content for: {request.topic}")
    print("Please wait — calling LLM...\n")

    content = generate_content(request)

    if content.auditory_content:
        ac = content.auditory_content
        print("Audio Narration Script (first 500 chars):")
        print(f"  {ac.audio_narration_script[:500]}...\n")
        print("Mnemonics:")
        for m in ac.mnemonics_and_songs:
            print(f"  • {m}")
        print("\nDiscussion Questions:")
        for dq in ac.discussion_questions:
            print(f"  • {dq}")
        print("\nStorytelling Narrative (first 300 chars):")
        print(f"  {ac.storytelling_narrative[:300]}...")

    return content


def demo_kinesthetic_content():
    """Stage 3 demo: Generate kinesthetic content for Acids and Bases."""

    print("\n" + "=" * 60)
    print("STAGE 3 — CONTENT GENERATOR (KINESTHETIC LEARNER)")
    print("=" * 60)

    request = ContentRequest(
        learning_style="kinesthetic",
        topic="Acids, Bases and Salts",
        subject="Chemistry",
        class_level="SS2",
        content_depth="core",
        student_id="stu_003",
    )

    print(f"\nGenerating kinesthetic content for: {request.topic}")
    print("Please wait — calling LLM...\n")

    content = generate_content(request)

    if content.kinesthetic_content:
        kc = content.kinesthetic_content
        print("Hands-On Activities:")
        for act in kc.hands_on_activities:
            print(f"  • {act}")
        print("\nReal-World Applications (Nigerian Context):")
        for rwa in kc.real_world_applications:
            print(f"  • {rwa}")
        print("\nExperiment/Simulation:")
        print(f"  {kc.experiment_or_simulation}")
        print("\nGroup Activity:")
        print(f"  {kc.group_activity}")

    return content


if __name__ == "__main__":
    print("LearNexo Content Engine — Example Usage")
    print("(Running all three learning style demos)\n")

    print("Choose a demo to run:")
    print("  1) Visual  — SS2 Mathematics, Quadratic Equations")
    print("  2) Auditory — SS1 Biology, Photosynthesis")
    print("  3) Kinesthetic — SS2 Chemistry, Acids and Bases")
    print("  4) Learning Path — SS2 Mathematics (visual learner)")
    print("  all) Run all demos\n")

    choice = input("Enter choice (1/2/3/4/all): ").strip().lower()

    if choice == "1":
        demo_visual_content()
    elif choice == "2":
        demo_auditory_content()
    elif choice == "3":
        demo_kinesthetic_content()
    elif choice == "4":
        demo_learning_path()
    elif choice == "all":
        demo_learning_path()
        demo_visual_content()
        demo_auditory_content()
        demo_kinesthetic_content()
    else:
        print("Invalid choice. Running visual demo by default.")
        demo_visual_content()
