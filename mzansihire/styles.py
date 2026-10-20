"""
styles.py - the MzansiHire look: editorial, left-aligned, full-width layout.

Fonts: Manrope (headings and text) + Source Serif 4 (intro text).
Colours: deep forest green, soft lime, warm paper white, plus a thin
South African flag stripe as a signature detail.
"""
import base64
import os
import re

import streamlit as st

FLAG_GRADIENT = (
    "linear-gradient(90deg,#E03C31 0 25%,#FFB81C 25% 50%,#007749 50% 75%,#001489 75% 100%)"
)
ASSETS = "assets"


def _html(text):
    """Squashes HTML onto one line so Markdown can't break it into code blocks."""
    return re.sub(r"\n\s*", "", text).strip()


@st.cache_data(show_spinner=False)
def image_uri(*names):
    """Returns a data URI for the first existing file in assets/, or ''."""
    for name in names:
        path = os.path.join(ASSETS, name)
        if os.path.exists(path):
            ext = name.rsplit(".", 1)[-1].lower()
            mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
            with open(path, "rb") as f:
                return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()
    return ""


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap');

/* ---------- base ---------- */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"],
button, input, textarea, select, label { font-family: 'Manrope', sans-serif; }
.stApp { background: #F7F6F2; color: #202D28; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
.block-container, [data-testid="stMainBlockContainer"] { max-width: 100% !important; padding: 0 5.7% 3rem 5.7% !important; }
h1, h2, h3, h4 { letter-spacing: -0.02em; color: #202D28; }
::selection { background: #D5E8A9; color: #202D28; }

/* ---------- Streamlit widgets in our style ---------- */
.stButton > button, .stFormSubmitButton > button, [data-testid^="stBaseButton"], [data-testid^="stBaseLinkButton"] {
  background: #172E27; color: #F7F6F2; border: 1px solid transparent; border-radius: 5px;
  font-weight: 700; font-size: 13px; min-height: 46px; padding: 0 22px; transition: transform .18s ease-out, background .18s ease-out; }
.stButton > button:hover, .stFormSubmitButton > button:hover, [data-testid^="stBaseButton"]:hover, [data-testid^="stBaseLinkButton"]:hover {
  background: #2F4B3E; color: #F7F6F2; border-color: transparent; }
.stButton > button:active { transform: scale(.98); }
.stButton > button p, .stFormSubmitButton > button p, [data-testid^="stBaseLinkButton"] p { color: inherit; }
.stButton > button:disabled { opacity: .5; }
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div { border-radius: 4px; background: #FCFCFA; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; border: 1px solid #D8DDD3 !important; border-radius: 7px; }
[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid #D8DDD3; border-radius: 6px; }
[data-testid="stAlert"] { border-radius: 5px; }
.stProgress > div > div > div > div { background: #6B8844; }
.stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 1px solid #D5DCD1; }
.stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 13px; padding: 14px 0; color: #637069; background: transparent; }
.stTabs [aria-selected="true"] { color: #202D28; }
.stTabs [data-baseweb="tab-highlight"] { background: #172E27; height: 2px; }

/* links in app text, and Apply buttons that were already visited */
[data-testid="stMarkdownContainer"] a { color: #3F6B2F; text-decoration: underline; text-underline-offset: 3px; }
[data-testid="stMarkdownContainer"] a:hover { color: #172E27; }
[data-testid^="stBaseLinkButton"], [data-testid^="stBaseLinkButton"] * { color: #F7F6F2 !important; text-decoration: none; }

.st-key-about_img [data-testid="stImage"] { width: 100% !important; }
.st-key-about_img img { width: 100% !important; height: 380px; object-fit: cover; border-radius: 6px; filter: saturate(.85); }

/* ---------- shared bits ---------- */
.stApp .mh a { color: inherit; text-decoration: none; }
.mh-flag { height: 6px; background: __FLAG__; }
.mh-eyebrow { display: block; font-size: 10px; font-weight: 700; letter-spacing: 1.8px; color: #637069; text-transform: uppercase; }
.mh-h2 { font-size: 35px; font-weight: 600; letter-spacing: -1.5px; line-height: 1.22; margin-top: 16px; color: #202D28; }
.stApp a.mh-btn { display: inline-flex; align-items: center; gap: 28px; min-height: 50px; padding: 15px 23px; background: #172E27;
  color: #F7F6F2; border-radius: 5px; font-size: 13px; font-weight: 700; text-decoration: none; transition: background .18s ease-out; }
.stApp a.mh-btn:hover { background: #2F4B3E; }
.stApp a.mh-btn-light { background: #D5E8A9; color: #172E27; }
.stApp a.mh-btn-light:hover { background: #E2EDC6; }
.stApp a.mh-link { display: inline-flex; gap: 9px; font-size: 12px; font-weight: 700; color: #202D28; }
.stApp a.mh-link:hover { text-decoration: underline; }

/* ---------- header ---------- */
.mh-header { height: 94px; padding: 0; display: flex; align-items: center; justify-content: space-between; background: #F7F6F2; }
.mh-brand { display: inline-flex; align-items: center; font-weight: 800; font-size: 26px; letter-spacing: -1.1px; color: #202D28; }
.mh-mark { height: 35px; width: 35px; display: inline-grid; place-items: center; border: 1px solid #AEBBB0; border-radius: 8px; margin-right: 10px;
  color: #172E27; font-size: 18px; font-weight: 800; letter-spacing: 0; }
.mh-brand .mh-light { font-weight: 500; }
.mh-dot { color: #6B8844; margin-left: 1px; }
.mh-nav { display: flex; align-items: center; gap: 34px; font-size: 13px; font-weight: 600; }
.stApp .mh-nav a { color: #637069; }
.stApp .mh-nav a:hover { color: #202D28; }
.stApp .mh-nav a.mh-cta { color: #202D28; padding: 13px 17px; border: 1px solid #B7C0B8; border-radius: 5px; }
.mh-user { font-size: 13px; font-weight: 600; color: #637069; }

/* ---------- landing hero ---------- */
.mh-hero { background: #172E27; color: #F7F6F2; padding: 0 5.7% 24px; }
.mh-hero .mh-flag { margin: 0 -5.7% 24px -5.7%; }
.mh-topline { display: flex; justify-content: space-between; font-size: 9px; letter-spacing: 1.6px; color: #BBC9C0; padding-bottom: 32px; border-bottom: 1px solid #41574A; }
.mh-status { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #D5E8A9; margin-right: 9px; }
.mh-hero-grid { display: grid; grid-template-columns: 1.25fr 1fr; gap: 8%; padding: 47px 0 45px; align-items: center; }
.mh-h1 { font-size: clamp(50px, 5.4vw, 82px); font-weight: 600; letter-spacing: -3.5px; line-height: 1.07; color: #F7F6F2; }
.mh-lime { color: #D5E8A9; }
.mh-lead { font-family: 'Source Serif 4', serif; font-size: 17px; line-height: 1.65; max-width: 400px; margin: 25px 0 27px; color: #C8D3CC; }
.mh-note { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #B3C3B8; margin-top: 16px; }
.mh-media { align-self: center; margin-top: 27px; }
.mh-index { font-size: 9px; letter-spacing: 1.6px; margin-bottom: 13px; color: #C4D1C7; }
.mh-photo { width: 100%; height: 330px; object-fit: cover; object-position: center; border-radius: 2px; filter: saturate(.8); display: block; }
.mh-photo-ph { width: 100%; height: 330px; border-radius: 2px; background: linear-gradient(135deg, #2F4B3E, #1d382e); display: grid; place-items: center;
  color: #8FA897; font-size: 12px; letter-spacing: 1px; text-align: center; padding: 20px; }
.mh-caption { display: flex; align-items: center; justify-content: space-between; font-family: 'Source Serif 4', serif; font-style: italic;
  font-size: 13px; padding: 16px 0; border-bottom: 1px solid #496051; color: #D3DDD3; }
.mh-media-bottom { display: flex; align-items: center; justify-content: space-between; padding-top: 27px; color: #A9BDAD; font-size: 10px; letter-spacing: 2px; line-height: 1.8; }
.mh-bigarrow { font-size: 70px; line-height: 1; color: #D5E8A9; font-weight: 300; }
.mh-hero-bottom { display: flex; justify-content: space-between; align-items: center; font-size: 9px; letter-spacing: 1.3px; border-top: 1px solid #41574A; padding-top: 22px; color: #AABCAF; }

/* ---------- how it works ---------- */
.mh-how { padding: 86px 5.7% 68px; background: #F7F6F2; }
.mh-sechead { display: flex; justify-content: space-between; align-items: flex-end; gap: 50px; }
.mh-sub { max-width: 270px; font-size: 13px; line-height: 1.7; color: #637069; }
.mh-steps { display: grid; grid-template-columns: repeat(4, 1fr); margin: 42px 0 32px; }
.mh-step { border-top: 1px solid #B8C3B9; padding: 23px 24px 0 0; }
.mh-step + .mh-step { padding-left: 24px; border-left: 1px solid #D5DCD1; }
.mh-step-num { font-size: 40px; letter-spacing: -2px; font-weight: 300; color: #66806B; margin-bottom: 27px; display: block; }
.mh-step-title { font-size: 17px; font-weight: 650; margin-bottom: 12px; color: #202D28; }
.mh-step-text { font-size: 13px; line-height: 1.8; color: #637069; max-width: 270px; }

/* ---------- feature story ---------- */
.mh-feature { padding: 63px 5.7% 68px; background: #EDEEE7; }
.mh-spread { display: grid; grid-template-columns: 1.2fr 1fr; gap: 11%; margin-bottom: 45px; }
.mh-intro { font-family: 'Source Serif 4', serif; font-size: 18px; line-height: 1.6; color: #202D28; }
.mh-list { margin: 25px 0; display: grid; gap: 16px; font-size: 13px; }
.mh-list span { display: flex; align-items: center; gap: 10px; }
.mh-list b { color: #6B8844; }
.mh-notice { display: flex; gap: 15px; border: 1px solid #C2CCB6; background: #E7EBDD; padding: 19px 22px; border-radius: 5px; color: #3C4E36; }
.mh-notice strong { font-size: 12px; }
.mh-notice div div { font-size: 12px; line-height: 1.75; margin-top: 5px; max-width: 900px; }

/* ---------- footer ---------- */
.mh-footer { padding: 48px 0 22px; display: grid; grid-template-columns: 1fr auto; gap: 36px; background: #F7F6F2; }
.mh-footer .mh-tag { font-size: 12px; color: #637069; margin: 12px 0 8px; }
.mh-fnav { display: flex; gap: 36px; align-items: flex-start; margin-top: 9px; font-size: 12px; }
.mh-fbottom { grid-column: 1 / -1; display: flex; justify-content: space-between; gap: 20px; border-top: 1px solid #D0D8CC; padding-top: 20px; font-size: 10px; color: #637069; }
.mh-fbottom a { text-decoration: underline; }

/* ---------- inner page heading + about page ---------- */
.mh-pagehead { padding: 40px 0 10px; }
.mh-pagehead .mh-title { font-size: clamp(32px, 4vw, 49px); line-height: 1.17; font-weight: 600; letter-spacing: -2px; margin: 15px 0; color: #202D28; }
.mh-pagehead .mh-lede { font-size: 14px; line-height: 1.8; color: #637069; max-width: 690px; }
.mh-aboutimg { width: 100%; height: 380px; object-fit: cover; border-radius: 6px; display: block; margin: 22px 0 6px; filter: saturate(.85); }
.mh-info { display: grid; grid-template-columns: 1fr 1.8fr; gap: 60px; padding: 45px 0; border-bottom: 1px solid #CED7C7; }
.mh-info .mh-h3 { font-size: 25px; letter-spacing: -.7px; font-weight: 600; color: #202D28; }
.mh-info .mh-p { font-size: 14px; line-height: 1.9; color: #637069; margin-bottom: 15px; }
.mh-process { padding-top: 40px; }
.mh-pitem { display: flex; gap: 45px; border-bottom: 1px solid #CDD6C5; padding: 28px 0; }
.mh-pnum { font-size: 49px; font-weight: 300; color: #A0B28E; line-height: 1; min-width: 70px; }
.mh-pitem .mh-h3 { font-size: 21px; margin-bottom: 12px; font-weight: 600; color: #202D28; }
.mh-pitem .mh-p { font-size: 13px; line-height: 1.9; color: #637069; max-width: 690px; }
.mh-panel { padding: 42px; background: #172E27; color: #F7F6F2; margin: 40px 0; border-radius: 6px; }
.mh-panel .mh-eyebrow { color: #BDD0B8; }
.mh-panel .mh-h3 { font-size: 31px; margin: 18px 0; letter-spacing: -1px; font-weight: 600; color: #F7F6F2; }
.mh-panel .mh-p { color: #C5D2C6; font-size: 14px; line-height: 1.9; max-width: 760px; margin-bottom: 14px; }
.mh-ctabox { background: #E9EDE2; border-left: 4px solid #172E27; border-radius: 5px; padding: 24px 26px; margin-top: 26px; }
.mh-ctabox .mh-h3 { font-size: 20px; font-weight: 600; color: #202D28; margin-bottom: 6px; }
.mh-ctabox .mh-p { font-size: 13px; color: #637069; line-height: 1.7; }

/* ---------- mobile ---------- */
@media (max-width: 900px) {
  .mh-hero-grid { gap: 5%; } .mh-h1 { font-size: 58px; letter-spacing: -2.5px; }
  .mh-steps { grid-template-columns: 1fr 1fr; gap: 30px 0; } .mh-info { gap: 25px; }
}
@media (max-width: 640px) {
  .mh-header { height: 76px; } .mh-brand { font-size: 23px; } .mh-nav a:not(.mh-cta) { display: none; }
  .mh-nav a.mh-cta { padding: 10px 12px; font-size: 12px; }
  .mh-hero-grid { grid-template-columns: 1fr; padding: 34px 0 30px; gap: 25px; }
  .mh-h1 { font-size: 46px; letter-spacing: -2px; } .mh-topline span:last-child, .mh-media-bottom, .mh-hero-bottom > span { display: none; }
  .mh-photo, .mh-photo-ph { height: 220px; } .mh-hero-bottom { justify-content: flex-end; }
  .mh-how { padding: 55px 6%; } .mh-sechead { display: block; } .mh-h2 { font-size: 30px; } .mh-sub { max-width: 100%; margin-top: 20px; }
  .mh-steps { grid-template-columns: 1fr; gap: 30px; margin-top: 30px; } .mh-step, .mh-step + .mh-step { border-left: 0; padding: 20px 0 0; }
  .mh-feature { padding: 45px 6%; } .mh-spread { grid-template-columns: 1fr; gap: 25px; }
  .mh-footer { grid-template-columns: 1fr; } .mh-fnav { gap: 25px; }
  .mh-info { grid-template-columns: 1fr; gap: 20px; padding: 30px 0; } .mh-pitem { gap: 20px; } .mh-pnum { font-size: 37px; min-width: 50px; }
  .mh-panel { padding: 28px 22px; } .mh-aboutimg { height: 240px; }
}
</style>
"""

LANDING_CSS = """
<style>
.block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; }
.block-container [data-testid="stVerticalBlock"], [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] { gap: 0; }
.mh-header { padding: 0 5.7%; }
.mh-footer { padding: 48px 5.7% 22px; }
.st-key-auth_section { padding: 70px 5.7% 80px; background: #EDEEE7; }
.st-key-auth_section [data-testid="stVerticalBlock"] { gap: 1rem; }
@media (max-width: 640px) { .st-key-auth_section { padding: 45px 6% 55px; } }
</style>
"""


def inject_css(landing=False):
    css = CSS.replace("__FLAG__", FLAG_GRADIENT)
    if landing:
        css += LANDING_CSS
    css = re.sub(r"\n\s*\n", "\n", css)  # no blank lines: Markdown could cut the style block there
    st.markdown(css, unsafe_allow_html=True)


# ======================================================================
# Building blocks
# ======================================================================
def _brand():
    return '<span class="mh-brand"><span class="mh-mark">M</span>Mzansi<span class="mh-light">Hire</span><span class="mh-dot">.</span></span>'


def header(user_name=None):
    """Top bar. On the landing page it has links; after login it greets the user."""
    if user_name:
        right = f'<div class="mh-user">Signed in as {user_name}</div>'
    else:
        right = (
            '<div class="mh-nav"><a href="#how-it-works">How it works</a>'
            '<a href="#get-started">Sign in</a>'
            '<a class="mh-cta" href="#get-started">Build your profile ↗</a></div>'
        )
    st.markdown(_html(f'<div class="mh mh-header">{_brand()}{right}</div>'), unsafe_allow_html=True)


def page_heading(eyebrow, title, text=""):
    """Left-aligned editorial heading for inner pages."""
    lede = f'<div class="mh-lede">{text}</div>' if text else ""
    st.markdown(
        _html(f'<div class="mh mh-pagehead"><span class="mh-eyebrow">{eyebrow}</span>'
              f'<div class="mh-title" role="heading" aria-level="1">{title}</div>{lede}</div>'),
        unsafe_allow_html=True,
    )


def hero(title, subtitle="", pills=(), small=False, eyebrow="MZANSIHIRE"):
    """Kept for the app's existing pages: now renders the editorial page heading."""
    page_heading(eyebrow, title, subtitle)


def features():
    """No longer used (the landing page replaced it). Kept so old code does not crash."""
    return None


def _hero_block():
    img = image_uri(
        "5ede180f-8bda-468f-b841-299d6e528b07.webp",
        "home.png", "home.jpg", "home.jpeg", "home.webp", "hero.jpg",
    )
    if img:
        photo = f'<img class="mh-photo" src="{img}" alt="Young South African graduates working together on a laptop">'
    else:
        photo = '<div class="mh-photo-ph">Add your photo as assets/home.png</div>'
    return f"""
    <div class="mh mh-hero">
      <div class="mh-flag"></div>
      <div class="mh-topline"><span><span class="mh-status"></span> SKILL-FIRST. FUTURE-FOCUSED.</span><span>MADE WITH MZANSI IN MIND</span></div>
      <div class="mh-hero-grid">
        <div>
          <div class="mh-h1" role="heading" aria-level="1">Your skills.<br>Your future.<br><span class="mh-lime">Your next<br>opportunity.</span></div>
          <div class="mh-lead">You bring the potential. We match it to real South African vacancies. Upload your CV or list your skills, and see the jobs that fit.</div>
          <a class="mh-btn mh-btn-light" href="#get-started">Find matching jobs <span>↗</span></a>
          <div class="mh-note">✦ Free to join. We never keep your CV file.</div>
        </div>
        <div class="mh-media">
          <div class="mh-index">01 / THE NEXT CHAPTER</div>
          {photo}
          <div class="mh-caption"><span>Big ambitions start with a small step.</span><span>↗</span></div>
          <div class="mh-media-bottom"><span>YOUR SKILLS ARE<br>A STARTING POINT.</span><span class="mh-bigarrow">↗</span></div>
        </div>
      </div>
      <div class="mh-hero-bottom"><span>YOUR SKILLS. YOUR FUTURE. YOUR NEXT OPPORTUNITY.</span><a href="#how-it-works">Explore the process ↓</a></div>
    </div>
    """


def _how_block():
    return """
    <div class="mh mh-how" id="how-it-works">
      <div class="mh-sechead">
        <div><span class="mh-eyebrow">A LITTLE INPUT. A NEW PERSPECTIVE.</span>
        <div class="mh-h2" role="heading" aria-level="2">Potential, meet possibility.</div></div>
        <div class="mh-sub">No complicated setup. Four simple steps to explore what comes next.</div>
      </div>
      <div class="mh-steps">
        <div class="mh-step"><span class="mh-step-num">01</span><div class="mh-step-title">Tell us what you bring.</div>
          <div class="mh-step-text">Add your skills, studies and interests, or upload your CV and we suggest the skills we find.</div></div>
        <div class="mh-step"><span class="mh-step-num">02</span><div class="mh-step-title">See your matches.</div>
          <div class="mh-step-text">We rank current South African vacancies by how closely they fit your profile.</div></div>
        <div class="mh-step"><span class="mh-step-num">03</span><div class="mh-step-title">Close the gaps.</div>
          <div class="mh-step-text">See which skills jobs mention that you are missing, with links to short courses.</div></div>
        <div class="mh-step"><span class="mh-step-num">04</span><div class="mh-step-title">Apply and keep track.</div>
          <div class="mh-step-text">Apply on the original advert, then save jobs and mark the ones you have applied for.</div></div>
      </div>
      <a class="mh-link" href="#get-started">Create your profile <span>↗</span></a>
    </div>
    """


def _feature_block():
    return """
    <div class="mh mh-feature">
      <div class="mh-spread">
        <div><span class="mh-eyebrow">MORE THAN A JOB TITLE</span>
        <div class="mh-h2" role="heading" aria-level="2">You are not a keyword.<br>But your skills tell a story.</div></div>
        <div>
          <div class="mh-intro">For students finding their feet, graduates taking their first step, and anyone exploring a new path in South Africa.</div>
          <div class="mh-list">
            <span><b>✓</b> Matches shaped by your own profile and CV</span>
            <span><b>✓</b> Live South African vacancies with real Apply links</span>
            <span><b>✓</b> Skill-gap tips and short-course suggestions</span>
            <span><b>✓</b> Your CV file is never stored</span>
          </div>
          <a class="mh-btn" href="#get-started">Start with your skills <span>↗</span></a>
        </div>
      </div>
      <div class="mh-notice"><span>ⓘ</span><div><strong>Suggestions, not hiring decisions.</strong>
        <div>Matches show how closely the words on your profile fit a job advert. They are a starting point, not a promise of an interview. Always read the full advert before you apply.</div></div></div>
    </div>
    """


def landing_top():
    """Header, hero, how-it-works and feature story for the logged-out page."""
    st.markdown(_html(
        f'<div id="top"></div>' + '<div class="mh mh-header">' + _brand() +
        '<div class="mh-nav"><a href="#how-it-works">How it works</a><a href="#get-started">Sign in</a>'
        '<a class="mh-cta" href="#get-started">Build your profile ↗</a></div></div>'
        + _hero_block() + _how_block() + _feature_block()
    ), unsafe_allow_html=True)


def auth_intro():
    st.markdown(_html("""
    <div class="mh"><span class="mh-eyebrow">GET STARTED</span>
    <div class="mh-h2" role="heading" aria-level="2">Create your free profile.</div>
    <div class="mh-intro" style="margin-top:18px;max-width:430px">Sign up, add your skills or upload your CV, and see the jobs that fit you best.</div>
    <div class="mh-list" style="margin-top:22px"><span><b>✓</b> Matches ranked for you</span><span><b>✓</b> CV tips and skill-gap alerts</span><span><b>✓</b> Save jobs and track applications</span></div></div>
    """), unsafe_allow_html=True)


def footer():
    st.markdown(_html("""
    <div class="mh mh-flag"></div>
    <div class="mh mh-footer">
      <div>__BRAND__<div class="mh-tag">Built for potential. Guided by your skills.</div></div>
      <div class="mh-fnav"><a href="#how-it-works">How it works</a><a href="https://www.adzuna.co.za" target="_blank">Jobs by Adzuna ↗</a></div>
      <div class="mh-fbottom"><span>© 2026 MzansiHire</span><span>Suggestions, not hiring decisions.</span></div>
    </div>
    """.replace("__BRAND__", _brand())), unsafe_allow_html=True)
    