"""
recommender.py - the AI part of MzansiHire.

It reuses the approach from your notebook:
  1. Combine title + description + job_domain + level into one text field
  2. Clean the text (lowercase, letters only, tidy spaces)
  3. TF-IDF (stop_words='english', max_features=5000), FITTED ONCE on the jobs
  4. For a user: clean their profile, TRANSFORM it (never fit again), and
     rank jobs by cosine similarity

The jobs can come from the live Adzuna feed or from the prototype CSV.
This file has no Streamlit code in it, so you can test it on its own.
"""
import os
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = "data/LinkedIn_RDB_three.csv"

# Columns every job table must have (missing ones are filled with defaults)
DEFAULTS = {
    "title": "", "description": "", "job_location": "", "work_type": "",
    "job_domain": "Unknown", "level": "", "company": "", "apply_url": "",
    "province": "", "created": "",
}


def clean_text(text):
    """Same cleaning function as the notebook."""
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_csv_jobs(csv_path=DATA_PATH):
    """The prototype LinkedIn dataset, cleaned as in the notebook."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Job data not found at '{csv_path}'. "
            "Put LinkedIn_RDB_three.csv inside the data folder."
        )
    jobs = pd.read_csv(csv_path)
    jobs = jobs.drop(columns=["ben_pack_id"], errors="ignore")
    if "level" in jobs.columns:
        jobs["level"] = jobs["level"].fillna("Not Specified")
    return jobs


class JobRecommender:
    def __init__(self, jobs):
        if jobs is None or len(jobs) == 0:
            raise ValueError("There are no jobs to recommend from.")
        jobs = jobs.copy().reset_index(drop=True)

        for col, default in DEFAULTS.items():
            if col not in jobs.columns:
                jobs[col] = default
            jobs[col] = jobs[col].fillna(default).astype(str)
        jobs.loc[jobs["job_domain"].str.strip() == "", "job_domain"] = "Unknown"
        if "job_id" not in jobs.columns:
            jobs["job_id"] = jobs.index.astype(str)
        if "remote_allowed" not in jobs.columns:
            jobs["remote_allowed"] = False
        jobs["remote_allowed"] = jobs["remote_allowed"].astype(str).str.lower().eq("true")

        # --- Feature engineering + NLP cleaning ---
        combined = (
            jobs["title"] + " " + jobs["description"] + " "
            + jobs["job_domain"] + " " + jobs["level"]
        )
        jobs["cleaned_features"] = combined.apply(clean_text)

        # --- TF-IDF: fitted ONCE on the job postings ---
        self.tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.tfidf.fit_transform(jobs["cleaned_features"])
        self.jobs = jobs

    @classmethod
    def from_csv(cls, csv_path=DATA_PATH):
        return cls(load_csv_jobs(csv_path))

    # ------------------------------------------------------------------
    def filter_options(self):
        """Values for the filter drop-downs, taken from the real data."""
        def values(col):
            return sorted(v for v in self.jobs[col].unique() if str(v).strip())
        return {
            "levels": values("level"),
            "work_types": values("work_type"),
            "domains": values("job_domain"),
            "provinces": values("province"),
        }

    def recommend(self, profile_text, top_n=10, levels=None, work_types=None,
                  remote_only=False, domains=None, provinces=None):
        """Returns a DataFrame of the best-matching jobs (best first)."""
        cleaned = clean_text(profile_text)
        if not cleaned:
            return self.jobs.iloc[0:0].assign(similarity=[])

        # transform (NOT fit): reuse the vocabulary learned from the jobs
        user_vector = self.tfidf.transform([cleaned])
        scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        mask = pd.Series(True, index=self.jobs.index)
        if levels:
            mask &= self.jobs["level"].isin(levels)
        if work_types:
            mask &= self.jobs["work_type"].isin(work_types)
        if domains:
            mask &= self.jobs["job_domain"].isin(domains)
        if provinces:
            mask &= self.jobs["province"].isin(provinces)
        if remote_only:
            mask &= self.jobs["remote_allowed"]

        results = self.jobs.assign(similarity=scores)[mask.values]
        results = results[results["similarity"] > 0]  # drop jobs with no overlap
        results = results.sort_values("similarity", ascending=False).head(top_n)
        results["similarity"] = results["similarity"].round(3)
        return results


def build_profile_text(profile):
    """Turns the saved profile into one text string for matching.

    Only job-related fields are used. The picture, name and email
    are never part of the matching.
    """
    parts = [
        profile.get("skills", ""),
        profile.get("career_interests", ""),
        profile.get("qualification", ""),
        profile.get("experience_level", ""),
        profile.get("about", ""),
    ]
    return " ".join(p for p in parts if p)


def skills_in_job(skills_text, job_description):
    """Which of the user's own skills are mentioned in this job's text?"""
    found = []
    for skill in [s.strip() for s in skills_text.split(",") if s.strip()]:
        pattern = r"(?<![A-Za-z0-9])" + re.escape(skill) + r"(?![A-Za-z0-9])"
        if re.search(pattern, job_description, flags=re.IGNORECASE):
            found.append(skill)
    return found
