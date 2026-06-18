"""
Price section — L1 Price signals.

Three tabs (stubs in v1):
  - Where are the meaningful price drops?
  - What discount depth registers as a deal?
  - Who's inflating their anchor prices?
"""
import streamlit as st
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, todays_read, stub_block


inject_global_styles()

section_header(
    eyebrow="Section \u00b7 L1 Price signals",
    title="Price",
    intro="Where prices are moving across the Egyptian fashion market \u2014 "
          "the genuine moves, the manufactured ones, and the depth required "
          "to register as a real deal in your category right now.",
)

tab1, tab2, tab3 = st.tabs([
    "Price Drops",
    "Deal Depth",
    "Anchor Inflation",
])

with tab1:
    why_matters(
        "**Where are the meaningful price drops?** Genuine price drops are "
        "reductions below a product's first-observed price \u2014 not below a "
        "manipulable compare-at price. Tracking these in real time tells "
        "you which competitors are moving, by how much, and in which "
        "categories."
    )
    stub_block("Detailed view shipping in week 2 \u2014 see roadmap.")

with tab2:
    why_matters(
        "**What discount depth registers as a deal?** Discounts only "
        "\"register\" as deals above a category-specific threshold. Going "
        "15% off when the market floor is 25% buys nothing. This tab shows "
        "the current depth distribution in your category and where the "
        "threshold sits this week."
    )
    stub_block("Detailed view shipping in week 2 \u2014 see roadmap.")

with tab3:
    why_matters(
        "**Who's inflating their anchor prices?** When a brand raises its "
        "compare-at price while leaving the actual price unchanged, they're "
        "manufacturing a fake discount. Tracking compare-at independently "
        "of price catches this. Several Egyptian brands run this tactic "
        "regularly."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")
