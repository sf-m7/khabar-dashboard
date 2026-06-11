"""
Lifecycle section — L1 Lifecycle signals.
"""
import streamlit as st
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, stub_block


inject_global_styles()

section_header(
    eyebrow="Section \u00b7 L1 Lifecycle signals",
    title="Lifecycle",
    intro="The full SKU arc: when products launch, how long they last at full "
          "price, when they get marked down, when they disappear. The shape of "
          "a brand's product economics, derived from observation.",
)

tab1, tab2, tab3 = st.tabs([
    "What launched this week?",
    "How long are products lasting before markdown?",
    "Who's resetting their price anchors quietly?",
])

with tab1:
    why_matters(
        "Clustered launches across a 7-day window indicate a collection drop. "
        "Tracking these tells you each brand's launch cadence \u2014 when they "
        "refresh, what categories they're betting on, and how aggressive they "
        "are this season."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")

with tab2:
    why_matters(
        "Days between launch and first markdown is the SKU shelf-life metric \u2014 "
        "the single number that tells a brand or factory whether a design worked. "
        "Sub-30-day markdowns signal a planning failure; 120+ days signals "
        "a correct market read."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")

with tab3:
    why_matters(
        "When a product is delisted and reappears within 30 days under a new "
        "SKU ID with identical name and image, the brand is resetting its "
        "price anchor \u2014 erasing the original first-observed price. One of "
        "the most deceptive practices in the market, invisible to every other "
        "tool that doesn't do temporal identity matching."
    )
    stub_block("Detailed view shipping in week 4 \u2014 requires Phantom Restock "
               "signal (L1\u00b718) to be implemented in the scraper first.")
