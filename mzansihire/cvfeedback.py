"""
cvfeedback.py - simple, rule-based CV feedback.

This is a checklist of general CV good practice. It is NOT an ATS score:
we can't validate it against real applicant-tracking systems.
It has no Streamlit code, so it can be tested on its own.
"""
import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

import cv

# Headings we look for (a short line containing one of these words)
SECTION_WORDS = {
    "Profile summary": ["summary", "profile", "objective", "about me", "personal statement"],
    "Education": ["education", "qualification", "academic"],
    "Work experience": ["experience", "employment", "work history", "internship"],
    "Skills": ["skills", "competencies"],
    "Projects": ["projects", "portfolio"],
    "Certifications": ["certification", "certificate", "courses", "training"],
}

ACTION_VERBS = [
    "managed", "led", "developed", "created", "built", "designed", "implemented",
    "improved", "increased", "reduced", "organised", "organized", "coordinated",
    "analysed", "analyzed", "delivered", "launched", "trained", "supported",
    "achieved", "initiated", "presented", "planned", "produced", "resolved",
    "streamlined", "tutored", "taught", "completed", "established", "negotiated",
]

WEAK_PHRASES = [
    "responsible for", "duties included", "hard working", "hard-working",
    "team player", "references available", "curriculum vitae",
]

GENERIC_JOB_WORDS = {
    "experience", "work", "working", "years", "will", "role", "position", "ability",
    "required", "requirements", "strong", "skills", "team", "company", "candidate",
    "looking", "apply", "must", "able", "including", "related", "good", "knowledge",
    "job", "responsibilities", "opportunity", "excellent", "relevant", "need",
}

EMAIL_RE = r"[\w.+-]+@[\w-]+\.[\w.-]+"
PHONE_RE = r"(?<![\d+])(?:(?:\+|00)?27[\s-]?\(?0?\)?|0)[\s-]?\(?\d{2}\)?[\s-]?\d{3}[\s-]?\d{4}(?!\d)"
SA_ID_RE = r"(?<!\d)\d{13}(?!\d)"


def find_sections(text):
    """Which sections have a heading? A heading is a short line (max 4 words)."""
    found = set()
    for line in text.splitlines():
        norm = re.sub(r"[^a-z ]", " ", line.lower())
        norm = re.sub(r"\s+", " ", norm).strip()
        if not norm or len(norm.split()) > 4:
            continue
        for section, words in SECTION_WORDS.items():
            if any(w in norm for w in words):
                found.add(section)
    return found


def analyse(text):
    """Returns {'checks': [...], 'skills': [...], 'word_count': n, 'sections': [...]}"""
    lower = text.lower()
    words = re.findall(r"[A-Za-z']+", text)
    word_count = len(words)
    sections = find_sections(text)
    skills = cv.detect_skills(text)
    verbs = sum(1 for v in ACTION_VERBS if re.search(r"\b" + v + r"\b", lower))
    numbers = len(re.findall(r"\d+%|\d[\d,.]*", text))
    weak = [p for p in WEAK_PHRASES if p in lower]

    checks = []

    def add(label, passed, tip):
        checks.append({"label": label, "passed": bool(passed), "tip": tip})

    add("Email address", re.search(EMAIL_RE, text),
        "Add a professional email address near the top, such as firstname.surname@...")
    add("Phone number", re.search(PHONE_RE, text),
        "Add a phone number employers can reach you on (for example 082 123 4567).")
    add("Education section", "Education" in sections,
        "Add an Education heading with your qualification, institution and year.")
    add("Skills section", "Skills" in sections,
        "Add a Skills heading and list your key skills, such as tools and software.")
    add("Experience or projects", bool({"Work experience", "Projects"} & sections),
        "Graduates can use internships, projects, volunteering or part-time work. Add a heading for them.")
    add("Profile summary", "Profile summary" in sections,
        "Add a 2 to 3 line summary at the top: who you are, what you studied, what role you want.")
    add("Sensible length", 150 <= word_count <= 900,
        f"Your CV has about {word_count} words. Most graduate CVs fit on 1 to 2 pages (roughly 300 to 700 words).")
    add("Action verbs", verbs >= 5,
        "Start bullet points with verbs like developed, managed, organised, improved.")
    add("Numbers and results", numbers >= 3,
        "Add numbers where true, for example 'supported 30 customers a day' or 'improved marks by 10%'.")
    add("Recognised skills", len(skills) >= 5,
        "We found few skills we recognise. Name your tools and software clearly (for example Excel, Python, SAP).")
    add("Avoids weak phrases", not weak,
        "Try replacing these phrases with specific achievements: " + ", ".join(f"'{w}'" for w in weak) + ".")
    add("No ID number", not re.search(SA_ID_RE, text),
        "We spotted a 13-digit number that may be an ID number. Remove it from CVs you upload online "
        "(employers can ask for it later).")

    return {
        "checks": checks,
        "skills": skills,
        "word_count": word_count,
        "sections": sorted(sections),
    }


def compare_with_job(cv_text, job_text, n_words=8):
    """Compares a CV with a pasted job advert.

    Returns matched skills, missing skills (from our skills list) and
    other frequent words in the advert that the CV never uses.
    """
    cv_skills = cv.detect_skills(cv_text)
    job_skills = cv.detect_skills(job_text)
    cv_lower = {s.lower() for s in cv_skills}
    matched = [s for s in job_skills if s.lower() in cv_lower]
    missing = [s for s in job_skills if s.lower() not in cv_lower]

    cv_words = set(re.findall(r"[a-z]{4,}", cv_text.lower()))
    counts = Counter(
        w for w in re.findall(r"[a-z]{4,}", job_text.lower())
        if w not in ENGLISH_STOP_WORDS and w not in GENERIC_JOB_WORDS
    )
    missing_lower = {w for m in missing for w in re.findall(r"[a-z]+", m.lower())}
    other = [w for w, _ in counts.most_common()
             if w not in cv_words and w not in missing_lower][:n_words]
    return {"matched": matched, "missing": missing, "other_words": other}
