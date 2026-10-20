import io
import streamlit as st
from PIL import Image
import adzuna
import about
import db
import cv
import cvfeedback
import recommender
import skillgap
import styles
import tracker

st.set_page_config(page_title="MzansiHire", page_icon="🇿🇦", layout="wide")
db.init_db()
db.init_profiles()
tracker.init_tracker()
adzuna.init_jobs()
styles.inject_css(landing=st.session_state.get("user") is None)

if "user" not in st.session_state:
    st.session_state.user = None

QUALIFICATIONS = [
    "Matric / Grade 12",
    "National Certificate / N-Diploma",
    "Higher Certificate",
    "Diploma",
    "Bachelor's degree",
    "Honours degree",
    "Master's degree",
    "PhD",
    "Other",
]
EXPERIENCE_LEVELS = [
    "Student / no experience",
    "Recent graduate",
    "Entry level (0-2 years)",
    "Intermediate (3-5 years)",
    "Experienced (5+ years)",
]
MAX_PICTURE_MB = 2


def process_picture(uploaded_file):
    """Checks the picture is a real image under 2MB, shrinks it, returns (bytes, error)."""
    if uploaded_file.size > MAX_PICTURE_MB * 1024 * 1024:
        return None, f"Picture is too big. Please use one under {MAX_PICTURE_MB}MB."
    try:
        img = Image.open(uploaded_file).convert("RGB")
        img.thumbnail((400, 400))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue(), None
    except Exception:
        return None, "That file doesn't look like a valid image."


def profile_completeness(profile):
    """Percentage of profile fields filled in (a simple, honest progress measure)."""
    fields = ["skills", "qualification", "experience_level", "career_interests",
              "preferred_location", "about", "picture"]
    filled = sum(1 for f in fields if profile.get(f))
    return int(filled / len(fields) * 100)


def esc(text):
    """Stops '$' in job text from being treated as maths by Streamlit."""
    return str(text).replace("$", "\\$")


# ======================================================================
# Log in / sign up
# ======================================================================

def show_auth():
    styles.landing_top()
    st.markdown('<div id="get-started"></div>', unsafe_allow_html=True)

    with st.container(key="auth_section"):
        left, right = st.columns([1, 1], gap="large")

        with left:
            styles.auth_intro()

        with right:
            with st.container(border=True):
                tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

                with tab_login:
                    email = st.text_input("Email", key="login_email")
                    password = st.text_input("Password", type="password", key="login_pw")
                    if st.button("Log in", use_container_width=True):
                        user = db.verify_user(email, password)
                        if user:
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Incorrect email or password.")

                with tab_signup:
                    name = st.text_input("Full name", key="su_name")
                    email = st.text_input("Email", key="su_email")
                    password = st.text_input("Password (min 8 characters)", type="password", key="su_pw")
                    if st.button("Create account", use_container_width=True):
                        ok, msg = db.create_user(name, email, password)
                        (st.success if ok else st.error)(msg)

    styles.footer()

def old_show_auth():
    left, right = st.columns([3, 2], gap="large")

    with left:
        styles.hero(
            "Your skills. Your future. Matched.",
            "MzansiHire helps South African graduates and young job seekers "
            "find roles that fit what they can do.",
            pills=("🎓 Built for graduates", "🇿🇦 Made in Mzansi", "🆓 Free to use"),
        )

    with right:
        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

            with tab_login:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_pw")
                if st.button("Log in", use_container_width=True):
                    user = db.verify_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

            with tab_signup:
                name = st.text_input("Full name", key="su_name")
                email = st.text_input("Email", key="su_email")
                password = st.text_input("Password (min 8 characters)", type="password", key="su_pw")
                if st.button("Create account", use_container_width=True):
                    ok, msg = db.create_user(name, email, password)
                    (st.success if ok else st.error)(msg)

        styles.features()
    with st.expander("ℹ️ About MzansiHire"):
        about.about_content()
    styles.footer()


# ======================================================================
# Profile tab
# ======================================================================
def show_profile():
    user = st.session_state.user
    profile = db.get_profile(user["id"]) or {}

    # The skills box keeps its value in session state, so the CV upload
    # can fill it in before the user saves.
    skills_key = f"skills_input_{user['id']}"
    if skills_key not in st.session_state:
        st.session_state[skills_key] = profile.get("skills", "")

    if st.session_state.pop("profile_saved", False):
        st.success("Profile saved!")

    first_name = user["full_name"].split()[0]
    styles.hero(
        f"Welcome back, {first_name} 👋",
        "Let's get you job-ready. A complete profile means better matches.",
        small=True,
    )
    st.write("")

    col_card, col_form = st.columns([1, 2], gap="large")

    with col_card:
        with st.container(border=True):
            if profile.get("picture"):
                st.image(profile["picture"], width=140)
            else:
                st.markdown("<div style='font-size:5rem;text-align:center'>👤</div>", unsafe_allow_html=True)
            st.subheader(user["full_name"])
            st.caption(user["email"])
            pct = profile_completeness(profile)
            st.write(f"**Profile strength: {pct}%**")
            st.progress(pct / 100)
            if pct < 100:
                st.caption("Fill in every field and add a picture to reach 100%.")
            else:
                st.caption("Your profile is complete. 🎉")

    with col_form:
        # ---- CV upload (outside the form so it can fill in the skills box) ----
        with st.container(border=True):
            st.markdown("### 📄 Already have a CV?")
            st.caption(
                "Upload it and we'll suggest skills for your profile. PDF or DOCX, max "
                f"{cv.MAX_CV_MB}MB. We don't save your CV file. We only read the text "
                "to find skills, and you choose what to keep."
            )
            cv_file = st.file_uploader("Choose your CV", type=["pdf", "docx"], key="cv_file")
            if cv_file is not None and st.button("Find skills in my CV"):
                text, error = cv.extract_text(cv_file)
                if error:
                    st.error(error)
                else:
                    found = cv.detect_skills(text)
                    if not found:
                        st.warning(
                            "We couldn't recognise any skills in that CV. "
                            "Please type your skills in the box below."
                        )
                    else:
                        st.session_state[skills_key] = cv.merge_skills(
                            st.session_state[skills_key], found
                        )
                        st.success(
                            f"Found {len(found)} skills and added them to your Skills box below. "
                            "Please check them, remove any that are wrong, add any we missed, "
                            "then click Save profile."
                        )

        st.write("")

        # ---- The profile form ----
        with st.container(border=True):
            st.markdown("### Your profile")
            with st.form("profile_form"):
                skills = st.text_area(
                    "Your skills *",
                    key=skills_key,
                    placeholder="e.g. Python, Excel, data analysis, customer service, communication",
                    help="Separate skills with commas. This is the main text we use to match you to jobs.",
                )
                c1, c2 = st.columns(2)
                with c1:
                    qual_default = profile.get("qualification")
                    qualification = st.selectbox(
                        "Highest qualification",
                        QUALIFICATIONS,
                        index=QUALIFICATIONS.index(qual_default) if qual_default in QUALIFICATIONS else 4,
                    )
                with c2:
                    exp_default = profile.get("experience_level")
                    experience = st.selectbox(
                        "Experience level",
                        EXPERIENCE_LEVELS,
                        index=EXPERIENCE_LEVELS.index(exp_default) if exp_default in EXPERIENCE_LEVELS else 1,
                    )
                interests = st.text_input(
                    "Career interests",
                    value=profile.get("career_interests", ""),
                    placeholder="e.g. data analyst, software developer, marketing",
                )
                location = st.text_input(
                    "Preferred location (optional)",
                    value=profile.get("preferred_location", ""),
                    placeholder="e.g. Johannesburg, Cape Town, Remote",
                )
                about = st.text_area(
                    "About you (optional)",
                    value=profile.get("about", ""),
                    placeholder="A short summary of who you are and what you're looking for.",
                )
                picture_file = st.file_uploader(
                    "Profile picture (optional, PNG or JPG, max 2MB)",
                    type=["png", "jpg", "jpeg"],
                )
                st.caption("Your picture is only shown on your profile. It is never used to match or rank jobs.")
                submitted = st.form_submit_button("Save profile", use_container_width=True)

    if submitted:
        if len(skills.strip()) < 3:
            st.error("Please enter at least one skill.")
            return

        picture_bytes = None
        if picture_file is not None:
            picture_bytes, error = process_picture(picture_file)
            if error:
                st.error(error)
                return

        db.save_profile(
            user["id"],
            {
                "skills": skills.strip(),
                "qualification": qualification,
                "experience_level": experience,
                "career_interests": interests.strip(),
                "preferred_location": location.strip(),
                "about": about.strip(),
            },
            picture_bytes,
        )
        st.session_state.profile_saved = True
        st.rerun()


# ======================================================================
# Job matches tab
# ======================================================================
@st.cache_resource(show_spinner="Preparing the job matcher...")
def build_live_recommender(version):
    """Rebuilt only when the job list is refreshed (the version text changes)."""
    return recommender.JobRecommender(adzuna.load_jobs())


@st.cache_resource(show_spinner="Preparing the job matcher...")
def build_csv_recommender():
    return recommender.JobRecommender.from_csv()


def get_recommender():
    """Returns (matcher, is_live). Live South African jobs if we have them,
    otherwise the prototype CSV."""
    if adzuna.count_jobs() >= 20:
        return build_live_recommender(adzuna.last_refresh()), True
    return build_csv_recommender(), False


def refresh_panel(profile):
    """The 'Load latest South African jobs' button."""
    try:
        app_id = st.secrets["ADZUNA_APP_ID"]
        app_key = st.secrets["ADZUNA_APP_KEY"]
    except Exception:
        st.info(
            "To load live South African jobs, add your Adzuna keys to "
            ".streamlit/secrets.toml and restart the app."
        )
        return

    last = adzuna.last_refresh()
    hours = adzuna.hours_since_refresh()
    can_refresh = hours is None or hours >= adzuna.REFRESH_COOLDOWN_HOURS

    c1, c2 = st.columns([1, 2])
    with c1:
        clicked = st.button("🔄 Load latest SA jobs", disabled=not can_refresh)
    with c2:
        if last:
            st.caption(f"Jobs last updated: {last} UTC")
        else:
            st.caption("No live jobs loaded yet. Click the button to load them.")
        if not can_refresh:
            st.caption(
                f"You can refresh again in about {adzuna.REFRESH_COOLDOWN_HOURS - hours:.1f} hours "
                "(this protects the free allowance)."
            )

    if clicked:
        interests = [s.strip() for s in profile.get("career_interests", "").split(",") if s.strip()][:3]
        with st.spinner("Fetching jobs from Adzuna. This takes about 20 seconds..."):
            try:
                count, warning = adzuna.refresh(app_id, app_key, interests)
            except adzuna.AdzunaError as error:
                st.error(str(error))
                return
        message = f"Loaded jobs. We now have {count} South African jobs."
        if warning:
            message += " " + warning
        st.session_state["refresh_msg"] = message
        st.rerun()


def job_actions(user_id, job, status):
    """Apply / Save / 'I applied' buttons for one job card."""
    key = str(job.get("job_id", job.name))
    title = str(job["title"])
    company = str(job.get("company", "") or "")
    location = str(job["job_location"])
    apply_url = str(job.get("apply_url", "") or "")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if apply_url:
            st.link_button("Apply ↗", apply_url)
        else:
            st.caption("No apply link in the prototype data.")
    with c2:
        if status is None:
            st.button("💾 Save job", key=f"save_{key}", on_click=tracker.save_job,
                      args=(user_id, key, title, company, location, apply_url))
        elif status == "saved":
            st.button("✅ I applied", key=f"applied_{key}", on_click=tracker.mark_applied,
                      args=(user_id, key))
        else:
            st.caption("✅ Applied")
    with c3:
        if status == "saved":
            st.caption("Saved. Click 'I applied' after you apply.")


def show_matches():
    user = st.session_state.user
    profile = db.get_profile(user["id"])

    styles.hero(
        "Your job matches",
        "Jobs ranked by how closely their text matches your saved profile.",
        small=True,
    )
    st.write("")

    if st.session_state.get("refresh_msg"):
        st.success(st.session_state.pop("refresh_msg"))

    if not profile:
        st.info("Save your profile first (in the My profile tab), then your matches will appear here.")
        return

    refresh_panel(profile)

    try:
        rec, is_live = get_recommender()
    except FileNotFoundError as e:
        st.error(str(e))
        return

    if is_live:
        st.caption(
            "Live South African vacancies from [Adzuna](https://www.adzuna.co.za). "
            "Descriptions on Adzuna are short previews, so open the Apply link for the full advert."
        )
    else:
        st.warning(
            "Prototype data: no live jobs loaded yet, so these jobs come from a LinkedIn dataset "
            "that is not South Africa-specific. Click 'Load latest SA jobs' above."
        )

    options = rec.filter_options()
    with st.expander("Filters (optional)"):
        provinces = st.multiselect("Province", options["provinces"]) if options["provinces"] else []
        domains = st.multiselect("Category", options["domains"]) if len(options["domains"]) > 1 else []
        levels = st.multiselect("Job level", options["levels"]) if len(options["levels"]) > 1 else []
        work_types = st.multiselect("Work type", options["work_types"]) if len(options["work_types"]) > 1 else []
        remote_only = st.checkbox("Remote jobs only") if rec.jobs["remote_allowed"].any() else False
        top_n = st.slider("Number of results", 5, 30, 10)

    results = rec.recommend(
        recommender.build_profile_text(profile),
        top_n=top_n,
        levels=levels,
        work_types=work_types,
        remote_only=remote_only,
        domains=domains,
        provinces=provinces,
    )

    if results.empty:
        st.info("No matches found. Try adding more skills to your profile or removing some filters.")
        return

    my_skills = profile.get("skills", "")

    # ---- Skill-gap summary + pop-up notification ----
    job_texts = (results["title"] + " " + results["description"].astype(str)).tolist()
    gaps = skillgap.top_gaps(my_skills, job_texts)
    if gaps:
        top_names = ", ".join(name for name, _ in gaps[:3])
        toast_key = f"{user['id']}:{top_names}"
        if st.session_state.get("gap_toast_key") != toast_key:
            st.toast(f"Skill gap: your matches often mention {top_names}", icon="🧩")
            st.session_state["gap_toast_key"] = toast_key

        with st.container(border=True):
            st.markdown("### 🧩 Skills to build")
            st.caption("Skills these jobs mention that aren't in your profile yet.")
            for skill, count in gaps:
                links = " · ".join(f"[{n}]({u})" for n, u in skillgap.course_links(skill))
                st.markdown(f"**{skill}**: mentioned in {count} of {len(results)} jobs. Find a short course: {links}")
        st.write("")

    # ---- The job cards ----
    status_map = tracker.get_status_map(user["id"])
    st.write(f"**{len(results)} jobs found**")
    for _, job in results.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"#### {esc(job['title'])}")
                details = [job["company"], job["job_location"], job["job_domain"],
                           job["level"], job["work_type"]]
                st.caption(esc("  •  ".join(str(d) for d in details if str(d).strip())))
                if str(job["created"]).strip():
                    st.caption(f"🗓️ Posted {str(job['created'])[:10]}")
            with c2:
                st.metric("Text similarity", f"{job['similarity']:.3f}")

            description = str(job["description"])
            snippet = " ".join(description.split())[:300]
            st.markdown(esc(snippet) + "...")

            matched = recommender.skills_in_job(my_skills, description)
            if matched:
                st.success("Your skills mentioned in this job: " + ", ".join(matched))

            missing = skillgap.missing_skills(my_skills, job["title"] + " " + description)
            if missing:
                with st.expander("🧩 Skills you may be missing for this job"):
                    for skill in missing:
                        links = " · ".join(f"[{n}]({u})" for n, u in skillgap.course_links(skill))
                        st.markdown(f"**{skill}**: {links}")

            job_actions(user["id"], job, status_map.get(str(job.get("job_id", job.name))))

    st.caption(
        "Text similarity is how closely the words in your profile match the words in a job "
        "(0 to 1). It is a relevance signal, not your chance of being hired."
    )


# ======================================================================
# My applications tab
# ======================================================================
def show_applications():
    user = st.session_state.user
    styles.hero(
        "My applications",
        "Keep track of the jobs you've saved and the ones you've applied for.",
        small=True,
    )
    st.write("")

    saved = tracker.get_jobs(user["id"], "saved")
    applied = tracker.get_jobs(user["id"], "applied")

    st.markdown(f"### 💾 Saved ({len(saved)})")
    if not saved:
        st.caption("No saved jobs yet. Use Save job on the Job matches tab.")
    for job in saved:
        with st.container(border=True):
            st.markdown(f"**{esc(job['title'])}**")
            st.caption(esc(" • ".join(p for p in [job["company"], job["location"]] if p)))
            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                if job["apply_url"]:
                    st.link_button("Apply ↗", job["apply_url"])
            with b2:
                st.button("✅ I applied", key=f"s_applied_{job['job_key']}",
                          on_click=tracker.mark_applied, args=(user["id"], job["job_key"]))
            with b3:
                st.button("🗑️ Remove", key=f"s_remove_{job['job_key']}",
                          on_click=tracker.remove_job, args=(user["id"], job["job_key"]))

    st.markdown(f"### ✅ Applied ({len(applied)})")
    if not applied:
        st.caption("Jobs you mark as applied will appear here.")
    for job in applied:
        with st.container(border=True):
            st.markdown(f"**{esc(job['title'])}**")
            st.caption(esc(" • ".join(p for p in [job["company"], job["location"]] if p)))
            st.caption(f"Applied on {str(job['applied_at'])[:10]}")
            st.button("🗑️ Remove", key=f"a_remove_{job['job_key']}",
                      on_click=tracker.remove_job, args=(user["id"], job["job_key"]))

# ======================================================================
# CV feedback tab
# ======================================================================
def show_cv_feedback():
    styles.hero(
        "CV feedback",
        "Practical tips to make your CV clearer and stronger.",
        small=True,
    )
    st.write("")
    st.caption(
        "This is a checklist of general CV good practice. It is not an ATS score, because we "
        "can't test it against real employer systems. Your CV file is not saved. Its text is "
        "kept only while you are logged in and is cleared when you log out."
    )

    with st.container(border=True):
        cv_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"], key="cvfb_file")
        if cv_file is not None and st.button("Analyse my CV"):
            text, error = cv.extract_text(cv_file)
            if error:
                st.error(error)
            else:
                st.session_state["cvfb_text"] = text
                st.session_state["cvfb_result"] = cvfeedback.analyse(text)
                st.session_state.pop("cvfb_compare", None)

    result = st.session_state.get("cvfb_result")
    if not result:
        st.info("Upload your CV and click Analyse my CV to see your checklist.")
        return

    checks = result["checks"]
    passed = sum(1 for c in checks if c["passed"])
    st.markdown(f"### CV checklist: {passed} of {len(checks)} checks passed")
    st.progress(passed / len(checks))

    to_fix = [c for c in checks if not c["passed"]]
    good = [c for c in checks if c["passed"]]
    if to_fix:
        with st.container(border=True):
            st.markdown("#### ⚠️ To improve")
            for c in to_fix:
                st.markdown(f"**{c['label']}**: {esc(c['tip'])}")
    if good:
        with st.container(border=True):
            st.markdown("#### ✅ Looking good")
            for c in good:
                st.markdown(f"**{c['label']}**")

    if result["skills"]:
        st.caption("Skills we recognised in your CV: " + ", ".join(result["skills"]))
    st.caption(
        "Our checks can miss things in unusual layouts (columns, text boxes, images), "
        "so treat this as a guide and not a verdict."
    )

    # ---- Compare with a job advert ----
    st.write("")
    with st.container(border=True):
        st.markdown("### 🎯 Compare your CV with a job advert")
        st.caption(
            "Paste the text of a job advert to see which skills it mentions that your CV doesn't. "
            "Only add words to your CV that are true for you."
        )
        job_text = st.text_area("Job advert text", height=180, key="cvfb_job_text")
        if st.button("Compare with this job"):
            if len(job_text.strip()) < 30:
                st.error("Please paste more of the job advert.")
            else:
                st.session_state["cvfb_compare"] = cvfeedback.compare_with_job(
                    st.session_state["cvfb_text"], job_text
                )

        compare = st.session_state.get("cvfb_compare")
        if compare:
            if compare["matched"]:
                st.success("Skills in both the job and your CV: " + ", ".join(compare["matched"]))
            if compare["missing"]:
                st.warning("Skills the job mentions that your CV doesn't: " + ", ".join(compare["missing"]))
                for skill in compare["missing"][:5]:
                    links = " · ".join(f"[{n}]({u})" for n, u in skillgap.course_links(skill))
                    st.markdown(f"**{skill}**: find a short course: {links}")
            elif not compare["matched"]:
                st.info("We didn't recognise any skills from our list in that advert.")
            if compare["other_words"]:
                st.caption(
                    "Other words used in the advert but not in your CV: "
                    + ", ".join(compare["other_words"])
                    + ". Add them only if they honestly describe your experience."
                )


# ======================================================================
def show_home():
    styles.header(st.session_state.user["full_name"])
    tab_profile, tab_matches, tab_apps, tab_cv, tab_about = st.tabs(
        ["👤 My profile", "🎯 Job matches", "📌 My applications", "📝 CV feedback", "ℹ️ About"]
    )
    with tab_profile:
        show_profile()
    with tab_matches:
        show_matches()
    with tab_apps:
        show_applications()
    with tab_cv:
        show_cv_feedback()
    with tab_about:
        about.show_about()
    st.write("")
    if st.button("Log out"):
        st.session_state.clear()  # also forgets any CV-detected skills
        st.rerun()
    styles.footer()


if st.session_state.user is None:
    show_auth()
else:
    show_home()
