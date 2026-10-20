# MzansiHire

**AI-assisted job matching for South African graduates and young job seekers.**
Upload a CV or list your skills, and MzansiHire ranks current South African vacancies by how well they fit, shows the skills you are missing, and helps you apply and keep track.

- **Live app:** [paste your Streamlit link here]
- **Team:** Sky Blue 
- **Course:** BSc Computer Science, Artificial Intelligence module (CSIT 3rd-year project 2026)

---

## 1. The problem

Youth unemployment in South Africa is high, and graduates waste hours reading vacancies that do not fit their skills. MzansiHire reads the text of a job seeker's profile and of job adverts and matches the two.

## 2. Features

| Feature | What it does |
|---|---|
| Sign up and profile | Account with hashed password, skills, qualification, interests, profile picture |
| CV upload | Reads a PDF or DOCX in memory, detects skills and adds them to the profile (the file is not stored) |
| Job matches | Ranks live South African vacancies (Adzuna API) by TF-IDF cosine similarity, with filters |
| Skill gaps | Shows skills that top jobs mention but the profile lacks, with short-course search links |
| CV feedback | A 12-point checklist of CV good practice, plus a comparison of the CV with a pasted job advert |
| Apply and track | Apply opens the original advert; save jobs and mark them as applied |
| About page | Plain-language explanation of the project and privacy |


## . Method

**Pipeline:** CV + job data → NLP preprocessing → TF-IDF → matching and classification → jobs + feedback

## 3. How the AI works

1. **Text cleaning:** lowercase, letters only, tidy whitespace (same function in the notebook and the app).
2. **TF-IDF:** `TfidfVectorizer(stop_words="english", max_features=5000)` is **fitted once** on the job postings.
3. **Matching:** a user profile is cleaned, transformed with the already-fitted vectoriser (never refitted) and compared with every job by **cosine similarity**. The top jobs are shown.
4. **Supervised experiments (notebook):** a classifier that predicts a job's field from its text, used to train, tune and test properly.

### Results (from `MzansiHire_ML_Experiments.ipynb`)

- The neural network's loss falls steadily over 30 epochs and approaches zero, showing it converges.
- For IT, Sales, Engineering and Healthcare, **precision is 75% to 81%** and **recall reaches up to 91%**.
- The confusion matrix is concentrated on the diagonal, so the model rarely confuses one industry for another.
- Data: 6,328 LinkedIn job postings, cleaned to **5,446 jobs in 16 fields** (759 repeated adverts removed, label never used as an input, rare fields merged into "Other").
- Split: 70% train / 15% validation / 15% test (stratified, seed 42). The test set is used once.
- Models compared: baseline, Naive Bayes, Logistic Regression, Linear SVM, neural network (MLP), tuned with cross-validation.
- **Final model (tuned linear SVM) on the unseen test set:** accuracy **68.7%** (baseline 19.0%), macro-F1 **0.667**, macro precision 0.688, macro recall 0.658, ROC-AUC (one-vs-rest) **0.920**.
- **Recommender (same-field relevance proxy):** Precision@5 **0.478** against 0.094 for random jobs; Hit@5 81.6% against 37.0%.
  

## 4. Tech stack

Python 3.10+, Streamlit, scikit-learn, pandas, SQLite, bcrypt, pypdf, python-docx, Pillow, requests.

## 5. Project structure

```
app.py                 Streamlit pages and user flow
recommender.py         TF-IDF + cosine-similarity matcher
adzuna.py              Fetches and caches live South African jobs (Adzuna API)
cv.py                  CV reading (PDF/DOCX) and skill detection
cvfeedback.py          CV checklist and CV-vs-job comparison
skillgap.py            Missing skills and course links
tracker.py             Saved and applied jobs
db.py                  Users and profiles (SQLite, bcrypt)
styles.py, about.py    Look and feel, About page
assets/                Photos used by the pages
data/                  LinkedIn_RDB_three.csv(.gz) (fallback jobs) and the SQLite database (created at run time)
tests/test_core.py     55 automated tests
MzansiHire_ML_Experiments.ipynb   Data cleaning, EDA, features, models, tuning, results
manual_review_template.csv        Template for the manual relevance review
```

## 6. Runing it on  computer

```bash
pip install -r requirements.txt
``
1. [text](../mzansihire/data/LinkedIn_RDB_three.csv) 
2.  .streamlit/secrets.toml

   ADZUNA_APP_ID = "633837ca"
   ADZUNA_APP_KEY = "6b862b72d45b8da2aed3cb2d4f9b9164"

   ```
3. Starting the app:
   ```bash
   python -m streamlit run app.py
   ```
4. Sign up, upload a CV, create a profile, open **Job matches** and click **Load latest SA jobs**.

Without Adzuna keys the app still works, using the LinkedIn dataset as a fallback.


## 7. Installation

Requires **Python 3.9+**.

```bash
# Install dependencies
pip install pandas numpy scikit-learn matplotlib nltk
```

## 7. Runing the tests

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database and a fake Adzuna server, so no internet or keys are needed.
**Script:**
```bash
python main.py
```

The program loads the data, cleans it, trains the models, prints the evaluation metrics and shows the charts.



## 9. Privacy and security

- Passwords are hashed with bcrypt.
- Uploaded CVs are checked (type, first bytes, size, page count), read in memory and **not stored**.
- Name, picture and email are never used to match jobs.
- API keys are kept in a secrets file and never shown in error messages.

## 10. Limitations

- The LinkedIn dataset is mostly from the USA; it is used to develop and evaluate the methods. Live South African jobs come from Adzuna.
- Job-field labels overlap and are noisy; "same field" is only a proxy for relevance.
- Adzuna descriptions are short previews, so live matching has less text to use.
- A word-based matcher cannot judge seniority. The skills list is limited, and the CV checklist is general advice, not an ATS score.
- The manual relevance review  is still to be completed.

## 11. Next steps

South African training data, user feedback as relevance labels, sentence embeddings, seniority-aware ranking, approximate nearest-neighbour search for scale, and POPIA features (delete and export my data).

## 12. Data sources and credits

- Job postings (prototype): LinkedIn job listings dataset from Kaggle, file `LinkedIn_RDB_three.csv`.
- Live South African vacancies: **Jobs by [Adzuna](https://www.adzuna.co.za)** (used under their API terms; attribution shown in the app).
- Course links open search pages on Coursera, edX, Udemy and YouTube and are not endorsements.
