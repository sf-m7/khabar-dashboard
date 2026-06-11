"""
Khabar dashboard — main entry.

Flow:
  1. Inject global CSS so the login form is themed
  2. Gate on authentication (renders login form if not authenticated)
  3. Build the sidebar navigation
  4. Hand control to the chosen view
"""
import streamlit as st

from lib.styles import inject_global_styles
from lib.auth import require_login, current_user
from lib.components import brand_header_in_sidebar


# ─── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Khabar \u00b7 Intelligence",
    page_icon="\U0001F4D8",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# ─── Global styles ──────────────────────────────────────────────
inject_global_styles()

# ─── Auth gate ──────────────────────────────────────────────────
require_login()  # Stops here and renders the login form if not authenticated

# ─── Sidebar brand mark ─────────────────────────────────────────
with st.sidebar:
    brand_header_in_sidebar()

# ─── Navigation ─────────────────────────────────────────────────
user = current_user()

pages = {
    "": [
        st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    ],
    "L1 Diagnostic": [
        st.Page("views/price.py",       title="Price",       icon=":material/payments:"),
        st.Page("views/inventory.py",   title="Inventory",   icon=":material/inventory_2:"),
        st.Page("views/lifecycle.py",   title="Lifecycle",   icon=":material/cycle:"),
        st.Page("views/competitive.py", title="Competitive", icon=":material/visibility:"),
    ],
    "L2 Premium": [
        st.Page("views/intelligence.py", title="Intelligence", icon=":material/psychology:"),
    ],
    "Account": [
        st.Page("views/settings.py", title="Settings", icon=":material/settings:"),
    ],
}

pg = st.navigation(pages, position="sidebar")

# ─── Sidebar footer (signed-in user) ────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='position: fixed; bottom: 1.5rem; left: 1rem; right: 1rem; "
        f"font-family: \"JetBrains Mono\", monospace; font-size: 0.65rem; "
        f"color: var(--muted); letter-spacing: 1px; "
        f"border-top: 1px solid var(--border); padding-top: 1rem;'>"
        f"Signed in<br>"
        f"<span style='color: var(--ink);'>{user.get('username','')}</span><br>"
        f"<span style='font-size: 0.6rem;'>tier: {user.get('tier','basic')}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ─── Run the chosen page ────────────────────────────────────────
pg.run()
