"""
skillgap.py - finds skills a job mentions that the user's profile doesn't have,
and builds search links to short online courses.
"""
from collections import Counter
from urllib.parse import quote_plus

import cv

# Soft skills appear in almost every job, so they would just be noise here.
SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving", "time management",
    "critical thinking", "presentation skills", "adaptability", "creativity",
    "public speaking", "negotiation",
}


def _norm(text):
    return text.strip().lower()


def user_skill_set(skills_text):
    """Everything the user has listed, plus known skills detected in their text."""
    have = {_norm(s) for s in skills_text.split(",") if s.strip()}
    have |= {_norm(s) for s in cv.detect_skills(skills_text)}
    return have


def missing_skills(skills_text, job_text, max_items=6):
    """Known skills mentioned in the job text that are not in the user's profile."""
    have = user_skill_set(skills_text)
    gaps = [
        s for s in cv.detect_skills(job_text)
        if _norm(s) not in have and _norm(s) not in SOFT_SKILLS
    ]
    return gaps[:max_items]


def top_gaps(skills_text, job_texts, n=5):
    """The most common missing skills across several jobs: [(skill, count), ...]."""
    counter = Counter()
    for text in job_texts:
        counter.update(missing_skills(skills_text, text, max_items=100))
    return counter.most_common(n)


def course_links(skill):
    """Search links on learning platforms (search pages, not specific courses)."""
    q = quote_plus(skill)
    return [
        ("Coursera", f"https://www.coursera.org/search?query={q}"),
        ("edX", f"https://www.edx.org/search?q={q}"),
        ("Udemy", f"https://www.udemy.com/courses/search/?q={q}"),
        ("YouTube", f"https://www.youtube.com/results?search_query={quote_plus(skill + ' beginner course')}"),
    ]
