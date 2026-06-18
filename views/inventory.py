"""
Inventory section — L1 Inventory signals.

Tab 1 fully rebuilt with native HTML/CSS rendering — same design system
as the rest of the dashboard. No chart library. Bars, threshold lines,
and tables are all rendered as styled divs so they inherit Khabar's
design tokens directly.
"""
from html import escape
import streamlit as st
import pandas as pd

from lib.auth import current_user
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, todays_read, stub_block, empty_state
from lib.inventory_queries import (
    size_asymmetry, top_undersupply, generate_undersupply_read,
    stockout_matrix, CATEGORY_DISPLAY,
)


# ─── Design tokens (kept in sync with lib/styles.py) ────────────────
GOLD       = "#1473E6"   # primary accent (named GOLD for back-compat with call sites)
GOLD_DIM   = "#0D5BB8"
MUTED      = "#E1E1E1"
INK        = "#2C2C2C"
INK_MUTED  = "#6E6E6E"


BRAND_DISPLAY = {
    "lc_waikiki": "LC Waikiki", "town_team": "Town Team",
    "ravin": "Ravin",            "mens_club": "Men's Club",
    "tree": "Tree",              "dott_jeans": "Dott Jeans",
    "defacto": "DeFacto",
}


# ─── Reusable: stat tile and HTML bar chart ────────────────────────
def stat_tile(label: str, value, hint: str = ""):
    """Big-number tile used in the stat row at the top."""
    st.markdown(
        f"<div style='background:var(--surface);border:1px solid var(--border);"
        f"padding:1.25rem 1.5rem;height:100%;'>"
        f"  <div style='font-family:var(--mono);font-size:0.6rem;letter-spacing:2px;"
        f"        color:var(--muted);text-transform:uppercase;margin-bottom:0.5rem;'>"
        f"    {escape(label)}"
        f"  </div>"
        f"  <div style='font-family:var(--sans);font-size:2rem;font-weight:700;"
        f"        color:var(--ink);line-height:1;'>"
        f"    {escape(str(value))}"
        f"  </div>"
        + (f"  <div style='font-family:var(--mono);font-size:0.65rem;color:var(--muted);"
           f"        margin-top:0.4rem;letter-spacing:1px;'>{escape(hint)}</div>"
           if hint else "")
        + f"</div>",
        unsafe_allow_html=True,
    )


def render_hbars(rows, label_key, value_key, value_format="{:,.0f}",
                 color_func=None, max_val=None, label_width=80,
                 thresholds=None):
    """Render a horizontal bar chart as pure HTML.

    rows         list of dicts
    label_key    which dict key holds the row label
    value_key    which dict key holds the numeric value
    color_func   optional callable (value) -> hex color; defaults to gold
    max_val      manual scale max (else uses data max)
    thresholds   optional list of (value, label) tuples to render as
                 dashed vertical reference lines across the bar tracks
    """
    if not rows:
        return ""

    color_func = color_func or (lambda v: GOLD)
    values     = [float(r[value_key]) for r in rows]
    auto_max   = max(values) if values else 1
    max_val    = max_val or auto_max
    if max_val <= 0:
        max_val = 1

    # Threshold reference lines (dashed verticals over the bar track)
    threshold_html = ""
    if thresholds:
        for t_val, t_label in thresholds:
            left_pct = min(99, (t_val / max_val) * 100)
            threshold_html += (
                f"<div style='position:absolute;left:{left_pct:.1f}%;top:-4px;"
                f"bottom:-4px;width:1px;border-left:1px dashed rgba(44,44,44,0.35);"
                f"pointer-events:none;'></div>"
            )

    bar_rows = []
    for r in rows:
        v       = float(r[value_key])
        width   = (v / max_val) * 100 if max_val > 0 else 0
        color   = color_func(v)
        label   = str(r[label_key])
        val_str = value_format.format(v)

        bar_rows.append(
            f"<div style='display:grid;grid-template-columns:{label_width}px 1fr 64px;"
            f"gap:14px;align-items:center;padding:7px 0;'>"

            # Label (right-aligned)
            f"<div style='font-family:var(--mono);font-size:0.78rem;color:var(--ink);"
            f"text-align:right;letter-spacing:0.5px;'>{escape(label)}</div>"

            # Bar track + fill (+ threshold overlay)
            f"<div style='position:relative;height:26px;"
            f"background:var(--surface2);"
            f"border-left:1px solid var(--border);'>"
            f"  <div style='position:absolute;left:0;top:0;bottom:0;"
            f"       width:{width:.1f}%;background:{color};'></div>"
            f"  {threshold_html}"
            f"</div>"

            # Value (left-aligned, prominent)
            f"<div style='font-family:var(--mono);font-size:0.92rem;color:var(--ink);"
            f"font-weight:500;text-align:left;'>{val_str}</div>"

            f"</div>"
        )

    # Threshold legend
    legend_html = ""
    if thresholds:
        items = []
        for t_val, t_label in thresholds:
            items.append(
                f"<span style='font-family:var(--mono);font-size:0.65rem;"
                f"color:var(--muted);letter-spacing:1px;'>"
                f"┊&nbsp;{escape(t_label)} ({t_val})</span>"
            )
        legend_html = (
            f"<div style='display:flex;gap:1.5rem;justify-content:flex-end;"
            f"padding:0.5rem 0 0 0;border-top:1px solid var(--border);"
            f"margin-top:0.5rem;'>"
            + "".join(items) +
            f"</div>"
        )

    return (
        f"<div style='background:var(--surface);border:1px solid var(--border);"
        f"padding:1rem 1.5rem;'>"
        + "".join(bar_rows)
        + legend_html
        + f"</div>"
    )


# ─── Page ──────────────────────────────────────────────────────────
inject_global_styles()

section_header(
    eyebrow="Section \u00b7 L1 Inventory signals",
    title="Inventory",
    intro="What's moving fast, what's stuck, and what brands are quietly "
          "abandoning. Demand revelation, derived from variant-level stockout "
          "and restock observations across every brand we track.",
)

tab1, tab2, tab3 = st.tabs([
    "Where is the market under-supplying?",
    "What's stuck and not selling?",
    "Which sizes are quietly being abandoned?",
])


# ────────────────────────────────────────────────────────────────────
# TAB 1
# ────────────────────────────────────────────────────────────────────
with tab1:
    why_matters(
        "Sizes that stock out fast while others sit untouched reveal what the "
        "market actually wants \u2014 vs what brands chose to produce. The same "
        "pattern showing up across multiple brands isn't a one-brand mistake; "
        "it's a market-wide manufacturing blind spot you can exploit either by "
        "stocking those sizes early, securing them from suppliers, or pricing "
        "them above the category median."
    )

    # Filters
    user        = current_user()
    user_gender = (user.get("gender_focus") or "").lower() or None

    fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
    with fcol1:
        days = st.select_slider("Time window",
                                options=[7, 14, 30, 60, 90], value=30)
    with fcol2:
        gender_choice = st.selectbox(
            "Gender",
            options=["All", "men", "women", "unisex", "kids"],
            index=(["All", "men", "women", "unisex", "kids"].index(user_gender)
                   if user_gender in ["men", "women", "unisex", "kids"] else 0),
        )
    with fcol3:
        category_choice = st.selectbox(
            "Category",
            options=["All categories"] + sorted(CATEGORY_DISPLAY.keys()),
        )

    gender_filter   = None if gender_choice == "All"              else gender_choice
    category_filter = None if category_choice == "All categories" else category_choice

    # Today's Read
    todays_read(generate_undersupply_read(days=days, gender_filter=gender_filter))

    # Data
    matrix_rows = stockout_matrix(days=days, gender=gender_filter, category=category_filter)
    asym_rows   = size_asymmetry(days=days, gender=gender_filter, min_stockouts=20)
    top_rows    = top_undersupply(days=days, gender=gender_filter,
                                  category=category_filter, limit=10)

    # Stat tiles
    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    total_stockouts   = sum(r["stockout_count"] for r in matrix_rows) if matrix_rows else 0
    n_categories      = len(set((r["category"], r["gender"]) for r in matrix_rows)) if matrix_rows else 0
    top_asymmetry     = (float(asym_rows[0]["asymmetry_score"])
                         if asym_rows and asym_rows[0].get("asymmetry_score") else 0.0)
    top_asymmetry_cat = (f"{asym_rows[0]['category']} ({asym_rows[0]['gender'][:1].upper()})"
                         if asym_rows else "\u2014")

    s1, s2, s3 = st.columns(3)
    with s1: stat_tile("Stockouts in window", f"{total_stockouts:,}",
                       f"last {days} days, size-tracked only")
    with s2: stat_tile("Category-gender segments", str(n_categories),
                       "with enough data to score")
    with s3: stat_tile("Top asymmetry score",
                       f"{top_asymmetry:.2f}",
                       f"in {top_asymmetry_cat}")

    # ─── Chart 1: Where demand is concentrating ────────────────────
    st.markdown(
        "<div style='margin-top: 2.5rem;'>"
        "<div class='eyebrow'>Where demand is concentrating</div>"
        "<h3 style='margin: 0.3rem 0 0 0;'>Sizes ranked by stockout count</h3>"
        "<p style='color: var(--muted); margin: 0.4rem 0 1rem 0; font-size: 0.85rem;'>"
        "Top 12 sizes by total stockouts in the selected window. The longer the bar, "
        "the more often a variant of that size sold out \u2014 direct demand signal."
        "</p></div>",
        unsafe_allow_html=True,
    )

    if not matrix_rows:
        empty_state("No stockout activity matching these filters.")
    else:
        df_sizes = (pd.DataFrame(matrix_rows)
                    .groupby("size", as_index=False)["stockout_count"].sum()
                    .sort_values("stockout_count", ascending=False)
                    .head(12))

        st.markdown(
            render_hbars(
                rows=df_sizes.to_dict("records"),
                label_key="size",
                value_key="stockout_count",
                value_format="{:,.0f}",
                label_width=70,
            ),
            unsafe_allow_html=True,
        )

    # ─── Chart 2: Most dysfunctional categories ────────────────────
    st.markdown(
        "<div style='margin-top: 2.5rem;'>"
        "<div class='eyebrow'>Most dysfunctional categories</div>"
        "<h3 style='margin: 0.3rem 0 0 0;'>Asymmetry index, top 8</h3>"
        "<p style='color: var(--muted); margin: 0.4rem 0 1rem 0; font-size: 0.85rem;'>"
        "Coefficient of variation across sizes within each category. "
        "Below 0.7 = healthy spread. 0.7\u20131.0 = strong asymmetry (some sizes dominate). "
        "Above 1.0 = extreme asymmetry (chronic mismatch between production and demand)."
        "</p></div>",
        unsafe_allow_html=True,
    )

    if not asym_rows:
        empty_state("Not enough data to compute asymmetry for these filters.")
    else:
        # Build asymmetry rows
        adf_rows = []
        for r in asym_rows[:8]:
            adf_rows.append({
                "label": f"{r['category']} \u00b7 {(r['gender'] or '')[:1].upper()}",
                "score": float(r["asymmetry_score"]),
            })

        def asymmetry_color(v: float) -> str:
            if v >= 1.0: return GOLD       # extreme
            if v >= 0.7: return GOLD_DIM   # strong
            return MUTED                    # mild

        scale_max = max(1.2, max(r["score"] for r in adf_rows) + 0.1)

        st.markdown(
            render_hbars(
                rows=adf_rows,
                label_key="label",
                value_key="score",
                value_format="{:.2f}",
                color_func=asymmetry_color,
                max_val=scale_max,
                label_width=160,
                thresholds=[(0.7, "strong"), (1.0, "extreme")],
            ),
            unsafe_allow_html=True,
        )

    # ─── Opportunities table ───────────────────────────────────────
    st.markdown(
        "<div style='margin-top: 2.5rem;'>"
        "<div class='eyebrow'>Top under-supply opportunities</div>"
        "<h3 style='margin: 0.3rem 0 0 0;'>Specific brand \u00b7 category \u00b7 size combinations</h3>"
        "<p style='color: var(--muted); margin: 0.4rem 0 1rem 0; font-size: 0.85rem;'>"
        "The ten highest-stockout combinations in the window. \u201c% on discount\u201d "
        "tells you whether the demand was natural (low %) or discount-driven (high %). "
        "Low-discount, high-volume rows are the strongest under-supply signals."
        "</p></div>",
        unsafe_allow_html=True,
    )

    if not top_rows:
        empty_state("No qualifying opportunities for these filters.")
    else:
        rows_html = []
        for r in top_rows:
            brand_disp = BRAND_DISPLAY.get(r["brand"], r["brand"])
            disc_pct = 0
            if r.get("stockout_count") and r["stockout_count"] > 0:
                disc_pct = round(100 * (r.get("on_discount_count") or 0) / r["stockout_count"])

            # Highlight low-discount, high-volume rows (natural demand)
            row_emphasis = "color: var(--gold); font-weight: 500;" if disc_pct < 25 else "color: var(--ink);"

            rows_html.append(
                "<tr>"
                f"<td style='font-family:var(--mono);font-size:0.78rem;color:var(--gold);"
                f"padding:14px 16px;border-bottom:1px solid var(--border);'>"
                f"{escape(brand_disp)}</td>"
                f"<td style='font-size:0.88rem;padding:14px 16px;"
                f"border-bottom:1px solid var(--border);'>"
                f"<span style='color:var(--ink);'>{escape(r['category'])}</span>"
                f"  <span style='color:var(--muted);font-family:var(--mono);font-size:0.7rem;"
                f"     letter-spacing:1px;'>\u00b7 {escape((r['gender'] or '').upper())}</span>"
                f"</td>"
                f"<td style='font-family:var(--mono);font-size:0.9rem;text-align:center;"
                f"padding:14px 16px;border-bottom:1px solid var(--border);{row_emphasis}'>"
                f"{escape(r['size'] or '\u2014')}</td>"
                f"<td style='font-family:var(--mono);font-size:0.95rem;text-align:right;"
                f"padding:14px 16px;border-bottom:1px solid var(--border);color:var(--ink);"
                f"font-weight:500;'>{r['stockout_count']}</td>"
                f"<td style='font-family:var(--mono);font-size:0.85rem;text-align:right;"
                f"padding:14px 16px;border-bottom:1px solid var(--border);"
                f"color:{'var(--gold)' if disc_pct < 25 else 'var(--muted)'};'>"
                f"{disc_pct}%</td>"
                "</tr>"
            )

        header = (
            "<thead><tr>"
            "<th style='text-align:left;font-family:var(--mono);font-size:0.6rem;"
            "letter-spacing:2px;color:var(--muted);padding:14px 16px;"
            "border-bottom:1px solid var(--bright);text-transform:uppercase;'>Brand</th>"
            "<th style='text-align:left;font-family:var(--mono);font-size:0.6rem;"
            "letter-spacing:2px;color:var(--muted);padding:14px 16px;"
            "border-bottom:1px solid var(--bright);text-transform:uppercase;'>Category</th>"
            "<th style='text-align:center;font-family:var(--mono);font-size:0.6rem;"
            "letter-spacing:2px;color:var(--muted);padding:14px 16px;"
            "border-bottom:1px solid var(--bright);text-transform:uppercase;'>Size</th>"
            "<th style='text-align:right;font-family:var(--mono);font-size:0.6rem;"
            "letter-spacing:2px;color:var(--muted);padding:14px 16px;"
            "border-bottom:1px solid var(--bright);text-transform:uppercase;'>Stockouts</th>"
            "<th style='text-align:right;font-family:var(--mono);font-size:0.6rem;"
            "letter-spacing:2px;color:var(--muted);padding:14px 16px;"
            "border-bottom:1px solid var(--bright);text-transform:uppercase;'>% on discount</th>"
            "</tr></thead>"
        )

        st.markdown(
            "<table style='width:100%;border-collapse:collapse;"
            "background:var(--surface);border:1px solid var(--border);"
            "margin-top:0.5rem;'>"
            + header
            + "<tbody>" + "".join(rows_html) + "</tbody>"
            + "</table>"
            "<p style='color: var(--muted); font-size: 0.75rem; margin-top: 0.6rem;"
            "font-family: var(--mono); letter-spacing: 0.5px;'>"
            "Rows in gold = stockouts occurring mostly at full price (natural demand). "
            "Rows in cream = discount-driven stockouts."
            "</p>",
            unsafe_allow_html=True,
        )


# ────────────────────────────────────────────────────────────────────
# TAB 2 — stub
# ────────────────────────────────────────────────────────────────────
with tab2:
    why_matters(
        "Products at deep discount with all variants still in stock for 30+ "
        "days are dead stock \u2014 a design, fabric, or fit failure that's "
        "eating warehouse space. Knowing what's dying across the market tells "
        "you what to avoid producing or stocking."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")


# ────────────────────────────────────────────────────────────────────
# TAB 3 — stub
# ────────────────────────────────────────────────────────────────────
with tab3:
    why_matters(
        "When a brand stops restocking specific sizes (say, 38 and 40) while "
        "continuing to replenish others, they're abandoning that size \u2014 "
        "a silent customer-mix shift. Catching this early reveals where "
        "competitors are moving their bets."
    )
    stub_block("Detailed view shipping in week 3 \u2014 see roadmap.")
