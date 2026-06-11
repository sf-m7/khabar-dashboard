"""
Inventory section — L1 Inventory signals.

Tab 1 (proof-of-template) is the model every other L1 tab follows.
Rebuilt to use cleaner, more readable visualisations: stat tiles,
focused horizontal bar charts, and a clear opportunities table.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.auth import current_user
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, todays_read, stub_block, empty_state
from lib.inventory_queries import (
    size_asymmetry, top_undersupply, generate_undersupply_read,
    stockout_matrix, CATEGORY_DISPLAY,
)


# ─── Plotly defaults that match the Khabar aesthetic ───────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8e2d5", family="Barlow", size=13),
    margin=dict(l=10, r=30, t=10, b=30),
    hoverlabel=dict(
        bgcolor="#13191f",
        bordercolor="#d4a843",
        font=dict(family="JetBrains Mono", color="#e8e2d5", size=12),
    ),
    showlegend=False,
)

GOLD       = "#d4a843"
GOLD_DIM   = "#7a6228"
MUTED      = "#3a4452"
INK        = "#e8e2d5"
INK_MUTED  = "#6b7585"
BORDER     = "rgba(255,255,255,0.07)"


BRAND_DISPLAY = {
    "lc_waikiki": "LC Waikiki", "town_team": "Town Team",
    "ravin": "Ravin",            "mens_club": "Men's Club",
    "tree": "Tree",              "dott_jeans": "Dott Jeans",
    "defacto": "DeFacto",
}


def stat_tile(label: str, value, hint: str = ""):
    """Big-number tile used in the stat row at the top of the tab."""
    st.markdown(
        f"<div style='background:var(--surface);border:1px solid var(--border);"
        f"padding:1.25rem 1.5rem;height:100%;'>"
        f"  <div style='font-family:var(--mono);font-size:0.6rem;letter-spacing:2px;"
        f"        color:var(--muted);text-transform:uppercase;margin-bottom:0.5rem;'>"
        f"    {label}"
        f"  </div>"
        f"  <div style='font-family:var(--serif);font-size:2rem;font-weight:900;"
        f"        color:var(--ink);line-height:1;'>"
        f"    {value}"
        f"  </div>"
        + (f"  <div style='font-family:var(--mono);font-size:0.65rem;color:var(--muted);"
           f"        margin-top:0.4rem;letter-spacing:1px;'>{hint}</div>"
           if hint else "")
        + f"</div>",
        unsafe_allow_html=True,
    )


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
# TAB 1 — full build
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

    # ─── Filters ───────────────────────────────────────────────────
    user        = current_user()
    user_gender = (user.get("gender_focus") or "").lower() or None

    fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
    with fcol1:
        days = st.select_slider(
            "Time window",
            options=[7, 14, 30, 60, 90],
            value=30,
        )
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

    # ─── Today's Read ──────────────────────────────────────────────
    todays_read(generate_undersupply_read(days=days, gender_filter=gender_filter))

    # ─── Fetch data once ───────────────────────────────────────────
    matrix_rows = stockout_matrix(days=days, gender=gender_filter, category=category_filter)
    asym_rows   = size_asymmetry(days=days, gender=gender_filter, min_stockouts=20)
    top_rows    = top_undersupply(days=days, gender=gender_filter,
                                  category=category_filter, limit=10)

    # ─── Stat tiles ────────────────────────────────────────────────
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

    # ─── Chart 1: Where demand is concentrating ───────────────────
    st.markdown(
        "<div style='margin-top: 2.5rem;'>"
        "<div class='eyebrow'>Where demand is concentrating</div>"
        "<h3 style='margin: 0.3rem 0 0 0;'>Sizes ranked by stockout count</h3>"
        "<p style='color: var(--muted); margin: 0.4rem 0 1rem 0; font-size: 0.85rem;'>"
        "Top 12 sizes by total stockouts in the selected window. The higher the "
        "bar, the more often a variant of that size sold out — direct demand signal."
        "</p></div>",
        unsafe_allow_html=True,
    )

    if not matrix_rows:
        empty_state("No stockout activity matching these filters.")
    else:
        df_sizes = (pd.DataFrame(matrix_rows)
                    .groupby("size", as_index=False)["stockout_count"].sum()
                    .sort_values("stockout_count", ascending=False)
                    .head(12)
                    .sort_values("stockout_count", ascending=True))

        fig1 = go.Figure(data=go.Bar(
            x=df_sizes["stockout_count"],
            y=df_sizes["size"],
            orientation="h",
            marker=dict(color=GOLD, line=dict(width=0)),
            text=df_sizes["stockout_count"].astype(str),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=12, color=INK),
            hovertemplate="<b>Size %{y}</b><br>%{x} stockouts<extra></extra>",
            cliponaxis=False,
        ))
        fig1.update_layout(
            **PLOTLY_LAYOUT,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       zeroline=False, showticklabels=False,
                       title=None),
            yaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(family="JetBrains Mono", size=13, color=INK),
                       title=None),
            height=max(280, 38 * len(df_sizes) + 30),
        )
        st.plotly_chart(fig1, use_container_width=True, theme=None)

    # ─── Chart 2: Most dysfunctional categories ───────────────────
    st.markdown(
        "<div style='margin-top: 2.5rem;'>"
        "<div class='eyebrow'>Most dysfunctional categories</div>"
        "<h3 style='margin: 0.3rem 0 0 0;'>Asymmetry index, top 8</h3>"
        "<p style='color: var(--muted); margin: 0.4rem 0 1rem 0; font-size: 0.85rem;'>"
        "Coefficient of variation across sizes within each category. "
        "Below 0.7 = healthy spread. 0.7–1.0 = strong asymmetry (some sizes dominate). "
        "Above 1.0 = extreme asymmetry (chronic mismatch between production and demand)."
        "</p></div>",
        unsafe_allow_html=True,
    )

    if not asym_rows:
        empty_state("Not enough data to compute asymmetry for these filters.")
    else:
        adf = (pd.DataFrame(asym_rows).head(8)
               .assign(score_f=lambda d: d["asymmetry_score"].astype(float),
                       label=lambda d: d.apply(
                           lambda r: f"{r['category']} \u00b7 {r['gender']}", axis=1))
               .sort_values("score_f", ascending=True))

        # Bar colors: gold for >=1.0, dim gold for 0.7-1.0, muted for <0.7
        bar_colors = [
            GOLD if s >= 1.0 else (GOLD_DIM if s >= 0.7 else MUTED)
            for s in adf["score_f"]
        ]

        fig2 = go.Figure(data=go.Bar(
            x=adf["score_f"],
            y=adf["label"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=adf["score_f"].apply(lambda v: f"{v:.2f}"),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=12, color=INK),
            hovertemplate="<b>%{y}</b><br>asymmetry %{x:.2f}<extra></extra>",
            cliponaxis=False,
        ))
        # Threshold lines
        fig2.add_vline(x=0.7, line_dash="dot", line_color="rgba(255,255,255,0.15)",
                       annotation_text="strong (0.7)",
                       annotation_position="top",
                       annotation_font=dict(family="JetBrains Mono", size=10,
                                           color=INK_MUTED))
        fig2.add_vline(x=1.0, line_dash="dot", line_color="rgba(212,168,67,0.4)",
                       annotation_text="extreme (1.0)",
                       annotation_position="top",
                       annotation_font=dict(family="JetBrains Mono", size=10,
                                           color=GOLD))
        fig2.update_layout(
            **PLOTLY_LAYOUT,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       zeroline=False, range=[0, max(1.2, adf["score_f"].max() + 0.2)],
                       tickfont=dict(family="JetBrains Mono", size=11, color=INK_MUTED),
                       title=None),
            yaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(family="Barlow", size=13, color=INK),
                       title=None),
            height=max(280, 42 * len(adf) + 60),
        )
        st.plotly_chart(fig2, use_container_width=True, theme=None)

    # ─── Opportunities table ──────────────────────────────────────
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
        from html import escape

        rows_html = []
        for r in top_rows:
            brand_disp = BRAND_DISPLAY.get(r["brand"], r["brand"])
            disc_pct = 0
            if r.get("stockout_count") and r["stockout_count"] > 0:
                disc_pct = round(100 * (r.get("on_discount_count") or 0) / r["stockout_count"])

            # Highlight rows where stockouts happened MOSTLY at full price
            # (natural demand, not discount-driven) — the strongest signal.
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

        table_html = (
            "<table style='width:100%;border-collapse:collapse;"
            "background:var(--surface);border:1px solid var(--border);"
            "margin-top:0.5rem;'>"
            + header
            + "<tbody>" + "".join(rows_html) + "</tbody>"
            + "</table>"
            + "<p style='color: var(--muted); font-size: 0.75rem; margin-top: 0.6rem; "
              "font-family: var(--mono); letter-spacing: 0.5px;'>"
              "Rows in gold = stockouts occurring mostly at full price (natural demand). "
              "Rows in cream = discount-driven stockouts."
              "</p>"
        )
        st.markdown(table_html, unsafe_allow_html=True)


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