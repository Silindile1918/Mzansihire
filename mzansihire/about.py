"""
about.py - the About page: the story, how MzansiHire works, privacy and FAQ.
Plain language, editorial layout, with a photo.
"""
import streamlit as st
import styles


def _html(text):
    return styles._html(text)


def about_content(logged_in=False):
    # ---- Why we exist ----
    st.markdown(_html("""
    <div class="mh mh-info">
      <div class="mh-h3" role="heading" aria-level="2">Why MzansiHire exists</div>
      <div>
        <div class="mh-p">Finding a first job is hard. There are lots of vacancies, it is difficult to tell which ones really fit you, and it is not always clear what employers are looking for.</div>
        <div class="mh-p">MzansiHire was built to make that first step simpler for South African graduates and young job seekers. You tell us what you can do, and we show you the vacancies that fit best.</div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    # ---- How it works ----
    st.markdown(_html("""
    <div class="mh mh-process"><span class="mh-eyebrow">HOW IT WORKS</span>
      <div class="mh-pitem"><span class="mh-pnum">01</span><div><div class="mh-h3" role="heading" aria-level="2">Create your profile.</div>
        <div class="mh-p">Sign up for free and add your skills, qualification, career interests and a profile picture.</div></div></div>
      <div class="mh-pitem"><span class="mh-pnum">02</span><div><div class="mh-h3" role="heading" aria-level="2">Upload your CV.</div>
        <div class="mh-p">Already have a CV? Upload it and we suggest the skills we find. You check them and keep only what is right.</div></div></div>
      <div class="mh-pitem"><span class="mh-pnum">03</span><div><div class="mh-h3" role="heading" aria-level="2">Get your matches.</div>
        <div class="mh-p">We rank current South African vacancies by how well they fit the skills and experience on your profile, and show which of your skills each job mentions.</div></div></div>
      <div class="mh-pitem"><span class="mh-pnum">04</span><div><div class="mh-h3" role="heading" aria-level="2">Close the gaps and apply.</div>
        <div class="mh-p">See which skills to build, with links to short courses. Apply on the original advert, then save jobs and mark the ones you have applied for. Use CV feedback to polish your CV before you send it.</div></div></div>
    </div>
    """), unsafe_allow_html=True)

    # ---- Privacy panel ----
    st.markdown(_html("""
    <div class="mh mh-panel"><span class="mh-eyebrow">YOUR PRIVACY</span>
      <div class="mh-h3" role="heading" aria-level="2">Your information stays yours.</div>
      <div class="mh-p">We do not keep your CV file. We read it to suggest skills, and you decide what goes on your profile.</div>
      <div class="mh-p">Your password is stored in scrambled form, never as plain text.</div>
      <div class="mh-p">Your picture, name and email are never used to match you to jobs. Matching looks at skills, qualifications and interests only.</div>
      <div class="mh-p">We collect only what we need to give you matches.</div>
    </div>
    """), unsafe_allow_html=True)

    # ---- FAQ ----
    st.markdown(_html("""
    <div class="mh"><span class="mh-eyebrow">QUESTIONS</span>
    <div class="mh-h2" role="heading" aria-level="2" style="margin-bottom:18px">Frequently asked questions</div></div>
    """), unsafe_allow_html=True)
    with st.expander("Is MzansiHire free to use?"):
        st.write("Yes. Creating a profile, getting matches and using the CV tools are free.")
    with st.expander("Where do the jobs come from?"):
        st.write(
            "Current South African vacancies come from Adzuna, a job search website. When you click "
            "Apply, you go to the original advert to apply there. We never apply on your behalf."
        )
    with st.expander("How are my matches chosen?"):
        st.write(
            "We compare the words on your profile (your skills, qualification and interests) with the "
            "words in each job advert, and show the closest matches first. The similarity score is a "
            "guide to how well the wording fits. It is not a promise that you will get the job, "
            "so always read the full advert before applying."
        )
    with st.expander("How often are the jobs updated?"):
        st.write(
            "You can load the latest vacancies from the Job matches page. To keep things fast and fair, "
            "this can be done every few hours."
        )
    with st.expander("Is MzansiHire only for graduates?"):
        st.write(
            "It is designed with graduates and young job seekers in mind, but anyone looking for a job "
            "in South Africa can use it."
        )
    with st.expander("Can you guarantee my CV will pass an employer's screening?"):
        st.write(
            "No. Our CV feedback gives general tips, such as clear sections, contact details and "
            "results, but every employer is different, so we cannot promise how any employer's system "
            "will treat your CV."
        )

    # ---- Call to action ----
    if logged_in:
        message = "Open the My profile tab, add your skills or upload your CV, then check Job matches."
    else:
        message = "Create a free account and add your skills or upload your CV to see your matches."
    st.markdown(_html(
        f'<div class="mh mh-ctabox"><div class="mh-h3" role="heading" aria-level="2">Ready to find your match?</div>'
        f'<div class="mh-p">{message}</div></div>'
    ), unsafe_allow_html=True)


def show_about():
    """The About tab shown after login."""
    import os

    styles.page_heading(
        "THE STORY BEHIND MZANSIHIRE",
        "A clearer start to<br>your career.",
        "MzansiHire matches your skills to real, current South African vacancies, so you spend "
        "less time searching and more time applying.",
    )

    photo = None
    folder = "assets"
    if os.path.isdir(folder):
        files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        # prefer about..., then home..., then hero..., then any picture
        for prefix in ("about", "home", "hero", ""):
            match = [f for f in files if f.lower().startswith(prefix)]
            if match:
                photo = os.path.join(folder, sorted(match)[0])
                break

    if photo:
        with st.container(key="about_img"):
            st.image(photo)
    else:
        st.info("Photo not found. Save a picture as assets/about.png (next to app.py) to show it here.")

    about_content(logged_in=True)