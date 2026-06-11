"""
CSS injection. Imports Google Fonts and overrides Streamlit's defaults so the
dashboard reads as a continuation of the Khabar playbook aesthetic, not a
generic Streamlit app.

Design source: /mnt/project/khabar_intelligence_playbook.html
"""
import streamlit as st


CSS = """
<style>
/* ---- Google Fonts ------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Barlow:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---- Khabar tokens ------------------------------------------- */
:root {
  --void:     #080a0f;
  --deep:     #0d1117;
  --surface:  #13191f;
  --surface2: #1a2230;
  --border:   rgba(255, 255, 255, 0.07);
  --bright:   rgba(255, 255, 255, 0.14);
  --ink:      #e8e2d5;
  --muted:    #6b7585;
  --gold:     #d4a843;
  --amber:    #c87533;
  --red:      #c03a2b;
  --blue:     #2d7fc1;
  --green:    #2d9e6b;
  --purple:   #7c5cbf;

  --serif: 'Playfair Display', Georgia, serif;
  --sans:  'Barlow', sans-serif;
  --mono:  'JetBrains Mono', monospace;
}

/* ---- Hide Streamlit chrome ---------------------------------- */
#MainMenu               { visibility: hidden; }
footer                  { visibility: hidden; }
.stDeployButton         { display: none; }
header[data-testid="stHeader"] { background: transparent; }

/* ---- Base typography ---------------------------------------- */
html, body, [class*="css"] {
  font-family: var(--sans);
  font-weight: 300;
  color: var(--ink);
  background: var(--void);
}

h1, h2, h3 {
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--ink);
}

h1 { font-size: 2.4rem; line-height: 1.05; }
h2 { font-size: 1.7rem; line-height: 1.15; margin-top: 1.5rem; }
h3 { font-size: 1.2rem; line-height: 1.2; }

p, li {
  font-family: var(--sans);
  font-size: 0.95rem;
  line-height: 1.65;
}

code, pre, .mono {
  font-family: var(--mono) !important;
  font-size: 0.85rem;
}

/* ---- Eyebrows ------------------------------------------------ */
.eyebrow {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.75rem;
}

/* ---- Login page --------------------------------------------- */
.login-container {
  max-width: 360px;
  margin: 6rem auto 1.5rem auto;
  text-align: left;
}
.login-eyebrow {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 4px;
  color: var(--gold);
  margin-bottom: 1.5rem;
}
.login-title {
  font-family: var(--serif);
  font-size: 2.5rem;
  font-weight: 900;
  margin-bottom: 0.5rem;
}
.login-sub {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}
.stForm {
  max-width: 360px;
  margin: 0 auto;
}

/* ---- Today's Read callout (every tab uses this) ------------ */
.todays-read {
  background: var(--surface);
  border-left: 3px solid var(--gold);
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
}
.todays-read-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 3px;
  color: var(--gold);
  margin-bottom: 0.5rem;
}
.todays-read-body {
  font-family: var(--sans);
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--ink);
}

/* ---- Why this matters (fixed paragraph at top of every tab) */
.why-matters {
  color: var(--muted);
  font-style: italic;
  font-size: 0.92rem;
  line-height: 1.7;
  margin: 0.5rem 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

/* ---- Anomaly cards (home page feed) ------------------------ */
.anomaly-card {
  background: var(--deep);
  border: 1px solid var(--border);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: border-color 0.15s;
}
.anomaly-card:hover { border-color: var(--bright); }
.anomaly-card-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.6rem;
}
.anomaly-severity {
  font-size: 1rem;
}
.anomaly-category {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 2px;
  padding: 2px 8px;
  border: 1px solid var(--border);
}
.anomaly-category.price       { color: var(--gold);   border-color: rgba(212,168,67,0.3); }
.anomaly-category.inventory   { color: var(--green);  border-color: rgba(45,158,107,0.3); }
.anomaly-category.lifecycle   { color: var(--blue);   border-color: rgba(45,127,193,0.3); }
.anomaly-category.competitive { color: var(--red);    border-color: rgba(192,58,43,0.3); }
.anomaly-time {
  margin-left: auto;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--muted);
}
.anomaly-title {
  font-family: var(--serif);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}
.anomaly-body {
  font-size: 0.9rem;
  color: var(--ink);
  line-height: 1.55;
}
.anomaly-meta {
  margin-top: 0.6rem;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.5px;
}

/* ---- Empty state -------------------------------------------- */
.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--muted);
  font-style: italic;
}

/* ---- Tab navigation styling --------------------------------- */
.stTabs [data-baseweb="tab-list"] {
  gap: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono);
  font-size: 0.8rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
  background: transparent;
  padding: 0.6rem 0;
}
.stTabs [aria-selected="true"] {
  color: var(--gold) !important;
}

/* ---- Sidebar ------------------------------------------------ */
[data-testid="stSidebar"] {
  background: var(--deep);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h2 {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 3px;
  color: var(--muted);
  text-transform: uppercase;
  font-weight: 400;
  margin-top: 1.5rem;
}

/* ---- Buttons (login + actions) ------------------------------ */
.stButton button, .stFormSubmitButton button {
  background: var(--gold);
  color: var(--void);
  border: none;
  font-family: var(--mono);
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 0.6rem 1.2rem;
  font-weight: 500;
}
.stButton button:hover, .stFormSubmitButton button:hover {
  background: #e8bc54;
  color: var(--void);
}

/* ---- Input fields ------------------------------------------- */
input, .stTextInput input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--ink) !important;
  font-family: var(--sans);
}

/* ---- Brand wordmark in sidebar ------------------------------ */
.brand-mark {
  font-family: var(--serif);
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--gold);
  letter-spacing: -0.5px;
  padding: 0.5rem 0 1rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.brand-tagline {
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 3px;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: -1.4rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

/* ---- "Coming soon" stub blocks ------------------------------ */
.stub-block {
  background: var(--surface);
  border: 1px dashed var(--border);
  padding: 2rem;
  text-align: center;
  color: var(--muted);
  font-style: italic;
  margin: 1rem 0;
}
</style>
"""


def inject_global_styles():
    """Call once at the top of every page / view file."""
    st.markdown(CSS, unsafe_allow_html=True)
