"""
Intelligence section — L2 synthesised products.

The premium content. L1 sections are the diagnostic surface; this section
is the synthesis surface. Each product lives on its own dedicated page
within this section.
"""
import streamlit as st
from lib.styles import inject_global_styles
from lib.components import section_header, stub_block
from lib.auth import current_user


inject_global_styles()

section_header(
    eyebrow="Section \u00b7 L2 Synthesised intelligence",
    title="Intelligence",
    intro="Where the diagnostic L1 signals become decision-quality intelligence. "
          "Each product synthesises multiple signals plus historical observations "
          "into a deliverable you can act on or share.",
)

user = current_user()
tier = (user.get("tier") or "basic").lower()

st.markdown("<div class='eyebrow' style='margin-top: 1rem;'>"
            f"Your tier: {tier.upper()}</div>", unsafe_allow_html=True)

# Three entry-bundle L2 products for Persona 1 (Egyptian DTC founder)
products = [
    {
        "code":  "L2\u00b711",
        "name":  "Cross-Brand Trend Velocity Map",
        "desc":  "How fast trends propagate from premium brands down to mass-market. "
                 "Tells you when a trend has crossed the tipping point and when it's "
                 "exhausted.",
        "tier":  "basic",
        "ready": False,
    },
    {
        "code":  "L2\u00b708",
        "name":  "Brand Health \u2014 Tier View",
        "desc":  "Composite health score for the average brand in your tier this month. "
                 "Use it to infer where the tier is heading and where you sit relative "
                 "to peers.",
        "tier":  "basic",
        "ready": False,
    },
    {
        "code":  "L2\u00b703",
        "name":  "Competitor Promotional Strategy Decoder",
        "desc":  "Each brand's promotional playbook mapped from observed price moves. "
                 "Identifies who runs honest sales vs systematically inflated anchor "
                 "sales, plus pre-holiday tactics.",
        "tier":  "basic",
        "ready": False,
    },
    {
        "code":  "L2\u00b702",
        "name":  "Factory Production Blueprint",
        "desc":  "Per-category colour mix, size ratios, and target price bands derived "
                 "from cross-brand sell-through data. Built for manufacturers; available "
                 "to brands at higher tier.",
        "tier":  "pro",
        "ready": False,
    },
    {
        "code":  "L2\u00b706",
        "name":  "Supply Chain Stress Index",
        "desc":  "Composite score per brand tracking restock velocity decay, discount "
                 "escalation, and supply-cycle stress. Reveals operational health "
                 "before any public signal.",
        "tier":  "pro",
        "ready": False,
    },
    {
        "code":  "L2\u00b713",
        "name":  "Egyptian Consumer Wallet Allocator",
        "desc":  "Estimated wallet share by income tier across brands. The only "
                 "quantitative answer to \"what share went where this quarter?\" "
                 "derived entirely from revealed preference.",
        "tier":  "enterprise",
        "ready": False,
    },
]

# Group by tier
tier_levels = {"basic": 1, "pro": 2, "enterprise": 3}
user_level = tier_levels.get(tier, 1)

for p in products:
    has_access = tier_levels.get(p["tier"], 99) <= user_level
    status = "" if p["ready"] else "Coming soon"
    lock = "" if has_access else " \u00b7 UPGRADE TO " + p["tier"].upper()

    box_style = ("background: var(--surface); border: 1px solid var(--border); "
                 "padding: 1.5rem; margin-bottom: 1rem;")
    if not has_access:
        box_style += "opacity: 0.5;"

    st.markdown(
        f"<div style='{box_style}'>"
        f"  <div style='display:flex; align-items:center; gap:1rem;'>"
        f"    <span style='font-family: var(--mono); color: var(--gold); "
        f"          font-size: 0.7rem; letter-spacing: 2px;'>{p['code']}</span>"
        f"    <span style='font-family: var(--mono); color: var(--muted); "
        f"          font-size: 0.65rem; letter-spacing: 2px;'>{status}{lock}</span>"
        f"  </div>"
        f"  <h3 style='margin: 0.5rem 0; font-size: 1.1rem;'>{p['name']}</h3>"
        f"  <p style='color: var(--ink); font-size: 0.9rem; margin: 0;'>{p['desc']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
stub_block("First L2 product (Cross-Brand Trend Velocity Map) shipping in week 4 \u2014 "
           "see roadmap.")
