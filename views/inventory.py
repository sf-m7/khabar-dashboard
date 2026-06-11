"""
Inventory section — L1 Inventory signals.

Tab 1 is the proof-of-template — the model every other L1 tab follows:
  - Fixed question heading
  - Fixed "why this matters" paragraph
  - Dynamic "Today's Read" paragraph (generated server-side from real data)
  - 1-2 primary visualisations
  - 1 actionable opportunities table
  - Filters at the bottom

Tabs 2 and 3 remain stubs until weeks 3 and 4.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.auth import current_user
from lib.styles import inject_global_styles
from lib.components import section_header, why_matters, todays_read, stub_block, empty_state
from lib.inventory_queries import (
    stockout_matrix, size_asymmetry, top_undersupply, generate_undersupply_read,
    CATEGORY_DISPLAY,
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

    # ─── Filters (top of tab so they affect everything below) ───────
    user = current_user()
    user_gender = (user.get("gender_focus") or "").lower() or None
    user_cats   = user.get("categories") or []

    fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
    with fcol1:
        days = st.select_slider(
            "Time window",
            options=[7, 14, 30, 60, 90],
            value=30,
            help="Stockout events within this many days are included.",
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
            help="Narrow the heatmap and opportunities to a single category.",
        )

    gender_filter   = None if gender_choice == "All"            else gender_choice
    category_filter = None if category_choice == "All categories" else category_choice

    # ─── Today's Read (dynamic) ────────────────────────────────────
    read_text = generate_undersupply_read(days=days, gender_filter=gender_filter)
    todays_read(read_text)

    # ─── Heatmap: stockout counts by size × (category, gender) ─────
    matrix_rows = stockout_matrix(days=days, gender=gender_filter, category=category_filter)

    if not matrix_rows:
        empty_state("No stockout activity matching these filters in the time window.")
    else:
        df = pd.DataFrame(matrix_rows)

        # Natural size ordering — letter sizes first (XS → 7XL), then numeric
        LETTER_ORDER = ["XXS", "XS", "S", "M", "L", "XL",
                        "2XL", "3XL", "4XL", "5XL", "6XL", "7XL"]
        NUMERIC_ORDER = ["26", "28", "30", "32", "34", "36", "38", "40", "42",
                         "44", "46", "48", "50",
                         "6", "7", "8", "9", "10", "11", "12", "14", "16", "18"]
        FULL_ORDER = LETTER_ORDER + NUMERIC_ORDER

        def size_rank(s):
            try:
                return FULL_ORDER.index(s)
            except ValueError:
                return 999

        df["size_rank"] = df["size"].apply(size_rank)
        df = df[df["size_rank"] < 999].copy()  # drop unknown sizes
        df["col_label"] = df.apply(
            lambda r: f"{r['category']} \u00b7 {r['gender'][:1].upper()}", axis=1
        )

        # Two heatmaps — letter sizes (most data) and numeric sizes
        df_letter = df[df["size"].isin(LETTER_ORDER)]
        df_num    = df[df["size"].isin(NUMERIC_ORDER)]

        def build_heatmap(sub_df, size_order_subset, title_suffix):
            if sub_df.empty:
                return None
            pivot = sub_df.pivot_table(
                index="size", columns="col_label",
                values="stockout_count", aggfunc="sum", fill_value=0,
            )
            present_sizes = [s for s in size_order_subset if s in pivot.index]
            pivot = pivot.reindex(present_sizes)

            # Sort columns by total stockouts descending so the busiest categories sit left
            col_totals = pivot.sum(axis=0).sort_values(ascending=False)
            pivot      = pivot[col_totals.index]

            # Khabar-themed colorscale: dark void → gold for "hot" / high demand
            colorscale = [
                [0.00, "#0d1117"],   # void
                [0.20, "#13191f"],
                [0.45, "#5a4624"],
                [0.75, "#9a7530"],
                [1.00, "#d4a843"],   # gold
            ]

            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale=colorscale,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Stockouts", font=dict(color="#6b7585", size=10)),
                    tickfont=dict(color="#6b7585", size=9),
                    thickness=10,
                    len=0.7,
                ),
                hovertemplate=("<b>%{y}</b> in %{x}<br>"
                               "%{z} stockouts<extra></extra>"),
            ))
            fig.update_layout(
                title=dict(text=title_suffix, font=dict(color="#e8e2d5", size=13,
                                                       family="JetBrains Mono")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8e2d5", family="Barlow"),
                xaxis=dict(side="bottom", tickangle=-30, tickfont=dict(size=10)),
                yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                margin=dict(l=60, r=20, t=40, b=80),
                height=max(280, 28 * len(pivot.index) + 120),
            )
            return fig

        letter_fig = build_heatmap(df_letter, LETTER_ORDER, "Letter sizes \u2014 stockouts by category")
        num_fig    = build_heatmap(df_num,    NUMERIC_ORDER, "Numeric sizes \u2014 stockouts by category")

        if letter_fig:
            st.plotly_chart(letter_fig, use_container_width=True, theme=None)
        if num_fig:
            st.plotly_chart(num_fig, use_container_width=True, theme=None)

    # ─── Asymmetry index + Top opportunities ────────────────────────
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns([1, 1])

    # Asymmetry index bar chart (left)
    with bcol1:
        st.markdown("<div class='eyebrow' style='margin-bottom: 0.5rem;'>"
                    "Asymmetry index by category</div>", unsafe_allow_html=True)

        asym_rows = size_asymmetry(days=days, gender=gender_filter, min_stockouts=20)
        if not asym_rows:
            empty_state("Not enough data for asymmetry calculation.")
        else:
            adf = pd.DataFrame(asym_rows).head(10)
            adf["label"] = adf.apply(
                lambda r: f"{r['category']} ({r['gender'][:1].upper()})", axis=1
            )
            adf["score_f"] = adf["asymmetry_score"].astype(float)

            bar_fig = go.Figure(data=go.Bar(
                x=adf["score_f"],
                y=adf["label"],
                orientation="h",
                marker=dict(color="#d4a843"),
                hovertemplate=("<b>%{y}</b><br>asymmetry: %{x:.2f}<extra></extra>"),
            ))
            bar_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8e2d5", family="Barlow", size=11),
                xaxis=dict(
                    showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                    title="coefficient of variation",
                    title_font=dict(size=10, color="#6b7585"),
                ),
                yaxis=dict(autorange="reversed", showgrid=False),
                margin=dict(l=10, r=20, t=10, b=40),
                height=max(220, 32 * len(adf) + 50),
            )
            st.plotly_chart(bar_fig, use_container_width=True, theme=None)

    # Top 10 opportunities (right)
    with bcol2:
        st.markdown("<div class='eyebrow' style='margin-bottom: 0.5rem;'>"
                    "Top under-supply opportunities</div>", unsafe_allow_html=True)

        top_rows = top_undersupply(days=days, gender=gender_filter,
                                   category=category_filter, limit=10)

        if not top_rows:
            empty_state("No qualifying opportunities for these filters.")
        else:
            from html import escape

            BRAND_DISPLAY = {
                "lc_waikiki": "LC Waikiki", "town_team": "Town Team",
                "ravin": "Ravin", "mens_club": "Men's Club",
                "tree": "Tree", "dott_jeans": "Dott Jeans", "defacto": "DeFacto",
            }

            rows_html = []
            for r in top_rows:
                brand_disp = BRAND_DISPLAY.get(r["brand"], r["brand"])
                rows_html.append(
                    f"<tr>"
                    f"<td style='font-family:var(--mono);font-size:0.75rem;color:var(--gold);"
                    f"padding:8px 10px;border-bottom:1px solid var(--border);'>"
                    f"{escape(brand_disp)}</td>"
                    f"<td style='font-size:0.8rem;padding:8px 10px;border-bottom:1px solid var(--border);'>"
                    f"{escape(r['category'])} \u00b7 {escape((r['gender'] or '')[:1].upper())}</td>"
                    f"<td style='font-family:var(--mono);font-size:0.8rem;text-align:center;"
                    f"padding:8px 10px;border-bottom:1px solid var(--border);'>"
                    f"{escape(r['size'] or '\u2014')}</td>"
                    f"<td style='font-family:var(--mono);font-size:0.85rem;text-align:right;color:var(--ink);"
                    f"font-weight:500;padding:8px 10px;border-bottom:1px solid var(--border);'>"
                    f"{r['stockout_count']}</td>"
                    f"</tr>"
                )

            table_html = (
                "<table style='width:100%;border-collapse:collapse;"
                "background:var(--surface);border:1px solid var(--border);'>"
                "<thead><tr>"
                "<th style='text-align:left;font-family:var(--mono);font-size:0.65rem;"
                "letter-spacing:2px;color:var(--muted);padding:10px;border-bottom:1px solid var(--bright);'>"
                "BRAND</th>"
                "<th style='text-align:left;font-family:var(--mono);font-size:0.65rem;"
                "letter-spacing:2px;color:var(--muted);padding:10px;border-bottom:1px solid var(--bright);'>"
                "CATEGORY</th>"
                "<th style='text-align:center;font-family:var(--mono);font-size:0.65rem;"
                "letter-spacing:2px;color:var(--muted);padding:10px;border-bottom:1px solid var(--bright);'>"
                "SIZE</th>"
                "<th style='text-align:right;font-family:var(--mono);font-size:0.65rem;"
                "letter-spacing:2px;color:var(--muted);padding:10px;border-bottom:1px solid var(--bright);'>"
                "STOCKOUTS</th>"
                "</tr></thead><tbody>"
                + "".join(rows_html)
                + "</tbody></table>"
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