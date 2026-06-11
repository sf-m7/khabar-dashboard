"""
Auth for the Khabar dashboard.

User accounts live in the Supabase `dashboard_users` table. Passwords are
bcrypt-hashed. Login state lives in st.session_state.

Bootstrap flow: the very first time someone opens the deployed app, the
`dashboard_users` table is empty. The login screen detects this and turns
into a one-time "create first admin" form. After that, all future visits
see the normal login screen. New users beyond the first are created from
inside the dashboard (Settings → Add user, in a future iteration) or by
inserting rows directly in Supabase.
"""
import bcrypt
import streamlit as st
from datetime import datetime, timezone
from lib.db import get_client, safe_query


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def lookup_user(username: str):
    sb = get_client()
    rows = safe_query(
        sb.table("dashboard_users").select("*").eq("username", username).limit(1)
    )
    return rows[0] if rows else None


def users_exist() -> bool:
    """Return True if at least one user exists in the dashboard_users table."""
    sb = get_client()
    rows = safe_query(sb.table("dashboard_users").select("username").limit(1))
    return len(rows) > 0


def login(username: str, password: str) -> bool:
    user = lookup_user(username)
    if not user:
        return False
    if not verify_password(password, user.get("password_hash", "")):
        return False

    try:
        sb = get_client()
        sb.table("dashboard_users").update(
            {"last_login": datetime.now(timezone.utc).isoformat()}
        ).eq("username", username).execute()
    except Exception:
        pass

    st.session_state["user"] = {
        "username":     user["username"],
        "full_name":    user.get("full_name") or username,
        "company":      user.get("company") or "",
        "tier":         user.get("tier") or "basic",
        "categories":   user.get("categories") or [],
        "gender_focus": user.get("gender_focus") or "",
        "brand_tier":   user.get("brand_tier") or "",
        "watch_list":   user.get("watch_list") or [],
    }
    return True


def register_first_admin(username: str, password: str, full_name: str = "",
                         company: str = "") -> tuple[bool, str]:
    """Create the first admin. Only works when no users exist yet.

    Returns (success, message).
    """
    if users_exist():
        return False, "An account already exists. Use Sign in instead."

    username = (username or "").strip().lower()
    if not username:
        return False, "Username is required."
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username must contain only letters, numbers, hyphens, or underscores."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    sb = get_client()
    try:
        sb.table("dashboard_users").insert({
            "username":      username,
            "password_hash": hash_password(password),
            "full_name":     (full_name or username).strip(),
            "company":       (company or "").strip(),
            "tier":          "enterprise",   # First user gets the highest tier
        }).execute()
        return True, "Account created. Sign in below."
    except Exception as e:
        return False, f"Could not create account: {e}"


def logout():
    st.session_state.clear()
    st.rerun()


def is_authenticated() -> bool:
    return "user" in st.session_state


def current_user() -> dict:
    return st.session_state.get("user", {})


def _render_bootstrap_form():
    """One-time first-admin registration. Shown when no users exist."""
    st.markdown(
        "<div class='login-container'>"
        "<div class='login-eyebrow'>KHABAR \u00b7 FIRST-TIME SETUP</div>"
        "<h1 class='login-title'>Create your account</h1>"
        "<p class='login-sub'>This is the first time the dashboard is being used. "
        "Set up your admin account below \u2014 you can add more users later.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("bootstrap_form", clear_on_submit=False):
        username  = st.text_input("Choose a username (lowercase, no spaces)")
        password  = st.text_input("Choose a password (8+ characters)", type="password")
        password2 = st.text_input("Confirm password", type="password")
        full_name = st.text_input("Full name (optional)")
        company   = st.text_input("Company (optional)")
        submitted = st.form_submit_button("Create account", use_container_width=True)

        if submitted:
            if password != password2:
                st.error("Passwords don't match.")
            else:
                ok, msg = register_first_admin(username, password, full_name, company)
                if ok:
                    st.success(msg + " Refreshing\u2026")
                    st.rerun()
                else:
                    st.error(msg)

    st.stop()


def _render_login_form():
    """Normal login form. Shown when users already exist."""
    st.markdown(
        "<div class='login-container'>"
        "<div class='login-eyebrow'>KHABAR \u00b7 INTELLIGENCE</div>"
        "<h1 class='login-title'>Sign in</h1>"
        "<p class='login-sub'>Egyptian fashion retail intelligence.<br>"
        "By invitation only.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Username and password are required.")
            elif login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop()


def require_login():
    """Gate every view behind login.

    If the dashboard_users table is empty, show the one-time bootstrap form.
    Otherwise show the normal login form. Either way, this function only
    returns if the visitor is already authenticated.
    """
    if is_authenticated():
        return

    if not users_exist():
        _render_bootstrap_form()
    else:
        _render_login_form()
