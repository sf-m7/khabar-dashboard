"""
Settings — user preferences. All optional. Without these, the dashboard
works on sensible defaults (show everything, no watch-list filter).
"""
import streamlit as st
from lib.auth import current_user, logout
from lib.db import get_client
from lib.styles import inject_global_styles
from lib.components import section_header


inject_global_styles()

section_header(
    eyebrow="Account",
    title="Settings",
    intro="Preferences that personalise the anomaly feed and the dashboard's "
          "narrative. Everything here is optional \u2014 the dashboard still "
          "works fine without them.",
)

user = current_user()

st.markdown(f"**Signed in as:** {user.get('username','')} "
            f"({user.get('company','') or 'no company set'})")
st.markdown(f"**Subscription tier:** `{user.get('tier','basic')}`")

st.markdown("<h2 style='margin-top: 2rem;'>Preferences</h2>", unsafe_allow_html=True)

CATEGORIES = ["tops", "shirts", "polos", "sweatshirts", "hoodies", "cardigans",
              "sweaters", "jeans", "trousers", "shorts", "skirts", "leggings",
              "joggers", "jackets", "coats", "blazers", "dresses", "jumpsuits",
              "sneakers", "sandals", "boots", "bags", "accessories", "swimwear",
              "loungewear", "sportswear"]
TIERS = ["", "mass-market", "mid-range", "youth-focused", "premium"]
GENDERS = ["", "men", "women", "both", "kids"]
BRANDS = ["lc_waikiki", "town_team", "ravin", "mens_club", "tree", "dott_jeans", "defacto"]

with st.form("settings_form"):
    cats = st.multiselect(
        "Categories you sell in",
        options=CATEGORIES,
        default=user.get("categories") or [],
        help="Used to filter the anomaly feed and section views. Leave empty to see everything.",
    )
    tier = st.selectbox(
        "Your brand tier",
        options=TIERS,
        index=TIERS.index(user.get("brand_tier")) if user.get("brand_tier") in TIERS else 0,
        help="Anomalies and benchmarks are matched against your tier when relevant.",
    )
    gender = st.selectbox(
        "Gender focus",
        options=GENDERS,
        index=GENDERS.index(user.get("gender_focus")) if user.get("gender_focus") in GENDERS else 0,
    )
    watch = st.multiselect(
        "Watch-list (specific competitors you especially care about)",
        options=BRANDS,
        default=user.get("watch_list") or [],
        help="Anomaly feed will prioritise events from these brands. Leave empty to see all brands.",
    )

    saved = st.form_submit_button("Save preferences", use_container_width=False)

    if saved:
        sb = get_client()
        try:
            sb.table("dashboard_users").update({
                "categories":   cats,
                "brand_tier":   tier or None,
                "gender_focus": gender or None,
                "watch_list":   watch,
            }).eq("username", user["username"]).execute()

            # Update session state so the change is immediate
            st.session_state["user"]["categories"]   = cats
            st.session_state["user"]["brand_tier"]   = tier
            st.session_state["user"]["gender_focus"] = gender
            st.session_state["user"]["watch_list"]   = watch
            st.success("Preferences saved.")
        except Exception as e:
            st.error(f"Could not save preferences: {e}")

st.markdown("<h2 style='margin-top: 3rem;'>Session</h2>", unsafe_allow_html=True)

if st.button("Sign out"):
    logout()
