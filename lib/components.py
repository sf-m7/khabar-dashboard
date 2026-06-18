"""
Reusable UI components. Importing these keeps every view file short and
ensures the design stays consistent.
"""
import streamlit as st
from datetime import datetime, timezone
from html import escape


def section_header(eyebrow: str, title: str, intro: str = ""):
    """Top of every section page / view. Eyebrow + title + optional intro."""
    st.markdown(f"<div class='eyebrow'>{escape(eyebrow)}</div>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-top:0.1rem;'>{escape(title)}</h1>", unsafe_allow_html=True)
    if intro:
        st.markdown(f"<p style='color:var(--muted);max-width:680px;margin-top:0.4rem;'>{escape(intro)}</p>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin: 1rem 0; border-bottom: 1px solid var(--border);'></div>",
                unsafe_allow_html=True)


def why_matters(text: str):
    """The fixed 'why this matters' paragraph at the top of every tab.
    Supports a simple **bold** marker (escaped first, then converted to
    <strong>) so the lead question can be visually emphasized."""
    safe = escape(text)
    # Convert **bold** markers to <strong> after escaping, so this stays
    # safe against HTML injection while still allowing simple emphasis.
    parts = safe.split("**")
    rebuilt = ""
    for i, part in enumerate(parts):
        rebuilt += f"<strong>{part}</strong>" if i % 2 == 1 else part
    st.markdown(f"<div class='why-matters'>{rebuilt}</div>", unsafe_allow_html=True)


def todays_read(text: str):
    """The dynamic conclusion paragraph that updates with the data."""
    # Allow basic line breaks
    safe = escape(text).replace("\n", "<br>")
    st.markdown(
        f"<div class='todays-read'>"
        f"<div class='todays-read-label'>TODAY'S READ</div>"
        f"<div class='todays-read-body'>{safe}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def relative_time(iso_ts: str) -> str:
    """Convert an ISO timestamp into '4h ago' / '2d ago' format."""
    if not iso_ts:
        return ""
    try:
        ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - ts
        secs = int(delta.total_seconds())
        if secs < 60:        return f"{secs}s ago"
        if secs < 3600:      return f"{secs // 60}m ago"
        if secs < 86400:     return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:
        return ""


SEVERITY_ICON = {
    "urgent":     "🚨",
    "noteworthy": "⚠️",
    "trend":      "📈",
    "opportunity": "🔥",
    "info":       "📊",
}


def anomaly_card(severity: str, category: str, title: str, body: str,
                 meta: str = "", occurred_at: str = ""):
    """One anomaly card for the home feed.

    severity:     one of urgent, noteworthy, trend, opportunity, info
    category:     one of Price, Inventory, Lifecycle, Competitive
    title:        short one-line headline
    body:         1-2 sentence description
    meta:         optional small caption (e.g. signal name)
    occurred_at:  ISO timestamp; rendered as '4h ago'
    """
    icon = SEVERITY_ICON.get(severity, SEVERITY_ICON["info"])
    cat_class = category.lower()
    when = relative_time(occurred_at) if occurred_at else ""

    st.markdown(
        f"<div class='anomaly-card'>"
        f"  <div class='anomaly-card-header'>"
        f"    <span class='anomaly-severity'>{icon}</span>"
        f"    <span class='anomaly-category {cat_class}'>{escape(category.upper())}</span>"
        f"    <span class='anomaly-time'>{escape(when)}</span>"
        f"  </div>"
        f"  <div class='anomaly-title'>{escape(title)}</div>"
        f"  <div class='anomaly-body'>{escape(body)}</div>"
        + (f"  <div class='anomaly-meta'>{escape(meta)}</div>" if meta else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def empty_state(message: str):
    """Shown when a query returns no data."""
    st.markdown(f"<div class='empty-state'>{escape(message)}</div>", unsafe_allow_html=True)


def stub_block(message: str):
    """Placeholder for views not yet built."""
    st.markdown(f"<div class='stub-block'>{escape(message)}</div>", unsafe_allow_html=True)


def brand_header_in_sidebar():
    """The KHABAR wordmark lockup at the top of the sidebar.
    Bold heavy KHABAR with 'Intelligence' nested beneath it in a smaller,
    lighter weight — a single lockup, not two separate text blocks."""
    st.markdown(
        "<div class='brand-lockup'>"
        "  <div class='brand-mark'>KHABAR</div>"
        "  <div class='brand-sub'>Intelligence</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def account_footer_in_sidebar(tier: str):
    """Single unified container at the bottom of the sidebar: the brand
    lockup repeated small + the subscription tier. No username here —
    that lives in Settings only."""
    st.markdown(
        "<div class='sidebar-footer'>"
        "  <div class='sidebar-footer-brand'>"
        "    <span class='sidebar-footer-khabar'>KHABAR</span>"
        "    <span class='sidebar-footer-intel'>Intelligence</span>"
        "  </div>"
        f"  <div class='sidebar-footer-tier'>{escape(tier or 'basic')} tier</div>"
        "</div>",
        unsafe_allow_html=True,
    )
