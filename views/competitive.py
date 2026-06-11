"""
Competitive section — L1 Competitive signals.
"""
import streamlit as st
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, stub_block


inject_global_styles()

section_header(
    eyebrow="Section \u00b7 L1 Competitive signals",
    title="Competitive",
    intro="Cross-brand patterns: price wars, trend propagation, category "
          "trajectory. Only visible because we cover every major brand at "
          "once \u2014 a single-brand tracker cannot produce these signals.",
)

tab1, tab2, tab3 = st.tabs([
    "Is a price war brewing in my category?",
    "Where is my category heading?",
    "What trends are propagating across brands?",
])

with tab1:
    why_matters(
        "Price wars start subtle: one brand cuts, another responds within 48 "
        "hours, the first escalates. By the time the depth is obvious, the "
        "category margin floor has shifted. Catching the leader-follower "
        "dynamic early lets you decide whether to engage, hold, or de-escalate."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")

with tab2:
    why_matters(
        "Aggregated Brand Identity Drift across your tier tells you where the "
        "category is heading \u2014 upmarket, downmarket, niche, mass. Your "
        "brand's position relative to that arc is what determines whether "
        "you're with the wave or against it."
    )
    stub_block("Detailed view shipping in week 4 \u2014 requires Brand Identity "
               "Drift Index (L1\u00b723) to be implemented first.")

with tab3:
    why_matters(
        "When a colour, silhouette, or fabric cascades from premium-positioned "
        "brands down to mass-market within a 2-week window, the trend has "
        "crossed the mainstream tipping point. After that, ride-the-wave "
        "decisions get expensive."
    )
    stub_block("Detailed view shipping in week 4 \u2014 requires Cross-Brand "
               "Colour Migration (L1\u00b719) to be implemented first.")
