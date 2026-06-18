"""
Home view — anomaly feed.

The first thing the user sees after login. Three states:

  1. Active anomalies in the last 24h    → feed of cards
  2. Quiet day (no significant signals)  → weekly market pulse summary
  3. Authentication / data error         → empty state

Filtered by the user's preferences (watch list of brands).
"""
import streamlit as st
from datetime import datetime, timezone

from lib.auth import current_user
from lib.styles import inject_global_styles
from lib.components import section_header, anomaly_card, empty_state
from lib.queries import assemble_anomaly_feed, market_pulse_summary


inject_global_styles()

user = current_user()
display_name = user.get("full_name") or user.get("username") or "Operator"

# Time-of-day greeting
hour = datetime.now(timezone.utc).hour + 2  # rough Cairo offset (UTC+2)
hour = hour % 24
if   hour < 5:  greet = "Up late"
elif hour < 12: greet = "Good morning"
elif hour < 17: greet = "Good afternoon"
else:           greet = "Good evening"

section_header(
    eyebrow=f"{greet}, {display_name.split()[0]}",
    title="Today's anomalies",
    intro="What the market did in the last 24 hours that's worth your attention.",
)


feed = assemble_anomaly_feed(user=user)

if feed:
    for item in feed:
        anomaly_card(
            severity=item["severity"],
            category=item["category"],
            title=item["title"],
            body=item["body"],
            meta=item.get("meta", ""),
            occurred_at=item.get("occurred_at", ""),
        )
else:
    # Quiet day — show weekly pulse instead of an empty page
    pulse = market_pulse_summary(user=user)
    st.markdown(
        "<div class='empty-state' style='padding-bottom: 1rem;'>"
        "No significant anomalies in the last 24 hours."
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<h3 style='margin-top:0;'>Last 7 days, market pulse</h3>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Price drops", f"{pulse['price_drops_7d']:,}")
    with col2:
        st.metric("Stockouts", f"{pulse['stockouts_7d']:,}")
    with col3:
        st.metric("Product launches", f"{pulse['launches_7d']:,}")

    st.markdown(
        "<p style='color:var(--muted); font-size:0.85rem; margin-top:1rem;'>"
        "Use the sidebar to dig into a specific section.</p>",
        unsafe_allow_html=True,
    )
