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
from lib.components import account_footer_in_sidebar


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

# ─── Sidebar collapse state ──────────────────────────────────────
# CSS-only collapse: toggling a session flag adds/removes a class on the
# app wrapper. No hover-JS, no dependency on Streamlit DOM internals that
# could break on a version bump — just a class swap driven by a button.
# The toggle itself lives at the BOTTOM of the sidebar, grouped with the
# brand lockup and tier — not at the top.
if "sidebar_collapsed" not in st.session_state:
    st.session_state["sidebar_collapsed"] = False

collapsed = st.session_state["sidebar_collapsed"]

if collapsed:
    st.markdown(
        "<style>"
        "[data-testid='stSidebar'] { width: 76px !important; min-width: 76px !important; }"
        # Hide nav link text but keep the icon and its container visible.
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] li div[data-testid='stMarkdownContainer'] p "
        "{ display: none !important; }"
        # Force every icon glyph in the nav to render large and centered,
        # regardless of which internal testid this Streamlit version uses.
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] span.material-symbols-outlined, "
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] [data-testid='stIconMaterial'] "
        "{ font-size: 1.75rem !important; display: block !important; }"
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] li a "
        "{ display: flex !important; justify-content: center !important; "
        "  align-items: center !important; padding: 0.7rem 0 !important; }"
        # Hide section group labels ("L1 Diagnostic" etc.) — these render
        # as plain text rows (not <a> links) directly inside the nav list,
        # so target list items that contain no link as a structural rule
        # rather than guessing an internal class name.
        "[data-testid='stSidebar'] [data-testid='stSidebarNav'] li:not(:has(a)) "
        "{ display: none !important; }"
        # In the collapsed footer, hide everything except the toggle button.
        "[data-testid='stSidebar'] .sidebar-footer-intel, "
        "[data-testid='stSidebar'] .sidebar-footer-khabar, "
        "[data-testid='stSidebar'] .sidebar-footer-tier "
        "{ display: none !important; }"
        "[data-testid='stSidebar'] .sidebar-toggle-row "
        "{ justify-content: center !important; }"
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

# ─── Sidebar footer — brand lockup + tier + the collapse toggle, ────
# all grouped together at the bottom as one unit. Username intentionally
# NOT shown here; it lives in Settings.
with st.sidebar:
    account_footer_in_sidebar(user.get("tier", "basic"))
    toggle_label = "\u2192" if collapsed else "\u2190"
    st.markdown("<div class='sidebar-toggle-row'>", unsafe_allow_html=True)
    if st.button(toggle_label, key="sidebar_toggle"):
        st.session_state["sidebar_collapsed"] = not collapsed
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Run the chosen page ────────────────────────────────────────
pg.run()
