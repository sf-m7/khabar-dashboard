"""
CSS injection. Imports Google Fonts and overrides Streamlit's defaults so the
dashboard reads as a clean, minimal analytics workspace — restrained colour,
hairline borders, generous whitespace, in the spirit of Adobe Analytics.

Design source: white-minimalist restyle, June 2026.
"""
import streamlit as st


CSS = """
<style>
/* ---- Google Fonts ------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ---- Khabar tokens (white minimalist) ------------------------ */
:root {
  --canvas:     #FFFFFF;
  --surface:    #FAFAFA;
  --surface2:   #F2F2F2;
  --border:     #E1E1E1;
  --bright:     #C8C8C8;
  --ink:        #2C2C2C;
  --muted:      #6E6E6E;
  --accent:     #1473E6;
  --accent-soft:#E8F2FD;
  --accent-dim: #0D5BB8;
  --positive:   #2D9D78;
  --negative:   #D7373F;
  --warning:    #C9A227;

  /* legacy aliases kept so existing view files (which reference
     var(--gold) etc.) resolve to sane values without a full rewrite */
  --gold:    var(--accent);
  --amber:   var(--warning);
  --red:     var(--negative);
  --blue:    var(--accent);
  --green:   var(--positive);
  --purple:  #6B5CA5;
  --void:    var(--canvas);
  --deep:    var(--surface);

  --serif: 'Inter', -apple-system, sans-serif; /* serif retired; alias kept for old refs */
  --sans:  'Inter', -apple-system, sans-serif;
  --mono:  'JetBrains Mono', monospace;
}

/* ---- Hide Streamlit chrome ---------------------------------- */
#MainMenu               { visibility: hidden; }
footer                  { visibility: hidden; }
.stDeployButton         { display: none; }
header[data-testid="stHeader"] { background: transparent; }

/* ---- Base typography ------------------------------------------ */
html, body, [class*="css"] {
  font-family: var(--sans);
  font-weight: 400;
  color: var(--ink);
  background: var(--canvas);
}

[data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--canvas);
}

h1, h2, h3 {
  font-family: var(--sans);
  font-weight: 600;
  letter-spacing: -0.2px;
  color: var(--ink);
}

h1 { font-size: 1.9rem; line-height: 1.15; }
h2 { font-size: 1.3rem; line-height: 1.2; margin-top: 1.5rem; }
h3 { font-size: 1.05rem; line-height: 1.25; }

p, li {
  font-family: var(--sans);
  font-size: 0.92rem;
  line-height: 1.6;
  color: var(--ink);
}

code, pre, .mono {
  font-family: var(--mono) !important;
  font-size: 0.82rem;
}

/* ---- Eyebrows (small uppercase tracked labels) --------------- */
.eyebrow {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.6rem;
}

/* ---- Login page ----------------------------------------------- */
.login-container {
  max-width: 360px;
  margin: 6rem auto 1.5rem auto;
  text-align: left;
}
.login-eyebrow {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 2.5px;
  color: var(--accent);
  margin-bottom: 1.5rem;
}
.login-title {
  font-family: var(--sans);
  font-size: 2rem;
  font-weight: 700;
  color: var(--ink);
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
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 1.5rem;
}

/* ---- Today's Read callout (every tab uses this) -------------- */
.todays-read {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
}
.todays-read-label {
  font-family: var(--mono);
  font-size: 0.65rem;
  letter-spacing: 2.5px;
  color: var(--accent);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}
.todays-read-body {
  font-family: var(--sans);
  font-size: 1rem;
  line-height: 1.65;
  color: var(--ink);
}

/* ---- Why this matters (fixed paragraph at top of every tab) -- */
.why-matters {
  color: var(--ink);
  font-style: normal;
  font-size: 0.95rem;
  line-height: 1.65;
  margin: 0.75rem 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.why-matters strong {
  color: var(--ink);
  font-weight: 600;
}

/* ---- Anomaly cards (home page feed) --------------------------- */
.anomaly-card {
  background: var(--canvas);
  border: 1px solid var(--border);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.anomaly-card:hover {
  border-color: var(--bright);
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
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
  font-size: 0.62rem;
  letter-spacing: 1.5px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  text-transform: uppercase;
  background: var(--surface);
}
.anomaly-category.price       { color: var(--accent-dim); border-color: var(--accent-soft); background: var(--accent-soft); }
.anomaly-category.inventory   { color: #1F7A5C; border-color: #D7EFE5; background: #F1FAF6; }
.anomaly-category.lifecycle   { color: var(--accent-dim); border-color: var(--accent-soft); background: var(--accent-soft); }
.anomaly-category.competitive { color: #B23036; border-color: #FBE2E3; background: #FDF3F3; }
.anomaly-time {
  margin-left: auto;
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--muted);
}
.anomaly-title {
  font-family: var(--sans);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 0.3rem;
}
.anomaly-body {
  font-size: 0.88rem;
  color: var(--ink);
  line-height: 1.55;
}
.anomaly-meta {
  margin-top: 0.6rem;
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--muted);
  letter-spacing: 0.5px;
}

/* ---- Empty state ------------------------------------------------ */
.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--muted);
  font-style: normal;
}

/* ---- Tab navigation styling -------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
  gap: 1.75rem;
  border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono);
  font-size: 0.75rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
  background: transparent;
  padding: 0.6rem 0;
}
.stTabs [aria-selected="true"] {
  color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
  background-color: var(--accent) !important;
}

/* ---- Sidebar ------------------------------------------------------ */
[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h2 {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 2px;
  color: var(--muted);
  text-transform: uppercase;
  font-weight: 400;
  margin-top: 1.5rem;
}

/* ---- Buttons (login + actions) ------------------------------------ */
.stButton button, .stFormSubmitButton button {
  background: var(--accent);
  color: #FFFFFF;
  border: none;
  border-radius: 3px;
  font-family: var(--sans);
  font-size: 0.85rem;
  letter-spacing: 0.2px;
  text-transform: none;
  padding: 0.55rem 1.3rem;
  font-weight: 500;
}
.stButton button:hover, .stFormSubmitButton button:hover {
  background: var(--accent-dim);
  color: #FFFFFF;
}

/* ---- Input fields --------------------------------------------------- */
input, .stTextInput input {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  color: var(--ink) !important;
  font-family: var(--sans);
  border-radius: 3px;
}
input:focus, .stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent-soft) !important;
}

/* ---- Brand wordmark in sidebar --------------------------------------- */
.brand-mark {
  font-family: var(--sans);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.3px;
  padding: 0.5rem 0 1rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
/* ---- "Coming soon" stub blocks ----------------------------------------- */
.stub-block {
  background: var(--surface);
  border: 1px dashed var(--border);
  padding: 2rem;
  text-align: center;
  color: var(--muted);
  font-style: normal;
  margin: 1rem 0;
}

/* ---- Brand lockup (sidebar top): bold KHABAR, smaller Intelligence
   nested beneath it as one cohesive wordmark, not two separate lines -- */
.brand-lockup {
  padding: 0.4rem 0 1rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}
.brand-lockup .brand-mark {
  font-family: var(--sans);
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.3px;
  line-height: 1.1;
  border-bottom: none;
  padding: 0;
  margin: 0;
}
.brand-lockup .brand-sub {
  font-family: var(--sans);
  font-size: 0.78rem;
  font-weight: 400;
  color: var(--muted);
  letter-spacing: 0.2px;
  margin-top: -0.1rem;
}

/* ---- Unified sidebar footer: one container, brand (small) + tier only,
   no username (username lives in Settings only) ---------------------- */
.sidebar-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}
.sidebar-footer-brand {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  margin-bottom: 0.3rem;
}
.sidebar-footer-khabar {
  font-family: var(--sans);
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.1px;
}
.sidebar-footer-intel {
  font-family: var(--sans);
  font-size: 0.68rem;
  font-weight: 400;
  color: var(--muted);
}
.sidebar-footer-tier {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--accent);
}

/* ---- Sidebar collapse toggle: small circular icon button, fixed
   position at the top of the sidebar so it never shifts on collapse -- */
.sidebar-toggle-row {
  display: flex;
  justify-content: flex-end;
  padding: 0.25rem 0 0.75rem 0;
}
[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) {
  display: flex;
  justify-content: flex-end;
}
[data-testid="stSidebar"] button[kind="secondary"] {
  width: 2.1rem !important;
  height: 2.1rem !important;
  min-width: 2.1rem !important;
  padding: 0 !important;
  border-radius: 50% !important;
  background: var(--accent) !important;
  color: #FFFFFF !important;
  border: none !important;
  font-size: 1rem !important;
  line-height: 1 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
  background: var(--accent-dim) !important;
}
[data-testid="stSidebar"] button[kind="secondary"] p {
  margin: 0 !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
}

/* ---- Sidebar nav: more prominent icons -------------------------------- */
[data-testid="stSidebar"] [data-testid="stIconMaterial"] {
  font-size: 1.3rem !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
  padding-top: 0.55rem !important;
  padding-bottom: 0.55rem !important;
}

/* ---- Filter strip (Adobe Analytics pattern): filters sit on a visually
   distinct surface, separated from the chart canvas they control ------- */
.filter-strip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.85rem 1.1rem 0.3rem 1.1rem;
  margin: 0.75rem 0 1.25rem 0;
}
.filter-strip-label {
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.4rem;
}
.filter-strip [data-testid="stSelectbox"] label,
.filter-strip [data-testid="stSlider"] label {
  font-size: 0.75rem !important;
  color: var(--muted) !important;
}

/* ---- Tighter top-of-page spacing (denser, less mobile-stacked) ------- */
h1 + p, h1 + div p { margin-top: 0.3rem; }
.eyebrow + h1 { margin-top: 0.1rem; }
</style>
"""


def inject_global_styles():
    """Call once at the top of every page / view file."""
    st.markdown(CSS, unsafe_allow_html=True)
