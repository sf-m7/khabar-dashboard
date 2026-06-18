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
from lib.components import brand_header_in_sidebar, account_footer_in_sidebar


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

# ─── Sidebar collapse toggle ─────────────────────────────────────
# CSS-only collapse: toggling a session flag adds/removes a class on the
# app wrapper. No hover-JS, no dependency on Streamlit DOM internals that
# could break on a version bump — just a class swap driven by a button.
if "sidebar_collapsed" not in st.session_state:
    st.session_state["sidebar_collapsed"] = False

with st.sidebar:
    brand_header_in_sidebar()
    toggle_label = "\u00bb expand" if st.session_state["sidebar_collapsed"] else "\u00ab collapse"
    if st.button(toggle_label, key="sidebar_toggle", use_container_width=True):
        st.session_state["sidebar_collapsed"] = not st.session_state["sidebar_collapsed"]
        st.rerun()

if st.session_state["sidebar_collapsed"]:
    st.markdown("<div class='collapsed-marker'></div>", unsafe_allow_html=True)
    st.markdown(
        "<style>"
        "[data-testid='stSidebar'] { width: 72px !important; min-width: 72px !important; }"
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] span:not(.material-symbols-outlined) { display: none !important; }"
        "[data-testid='stSidebar'] .brand-lockup { display: none !important; }"
        "[data-testid='stSidebar'] .sidebar-footer-intel, "
        "[data-testid='stSidebar'] .sidebar-footer-khabar, "
        "[data-testid='stSidebar'] .sidebar-footer-tier { display: none !important; }"
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] [data-testid='stIconMaterial'] "
        "{ font-size: 1.6rem !important; }"
        "[data-testid='stSidebar'] button[kind='secondary'] p { font-size: 0.7rem !important; }"
        "</style>",
        unsafe_allow_html=True,
    )

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

# ─── Sidebar footer — one unified container, brand + tier only ──
# Username is intentionally NOT shown here; it lives in Settings.
with st.sidebar:
    account_footer_in_sidebar(user.get("tier", "basic"))

# ─── Run the chosen page ────────────────────────────────────────
pg.run()
