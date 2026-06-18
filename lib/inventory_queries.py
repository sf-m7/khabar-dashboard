"""
Queries powering the Inventory > Where is the market under-supplying? tab.

These call the dashboard_* RPC functions deployed in Supabase, which do the
heavy aggregation server-side. Each function here returns a list of dicts
ready for pandas / plotly.
"""
from lib.db import get_client


def stockout_matrix(days: int = 30, gender: str | None = None,
                    category: str | None = None) -> list[dict]:
    """Return rows of (size, category, gender, stockout_count, on_discount_count)."""
    sb = get_client()
    try:
        res = sb.rpc("dashboard_stockout_matrix", {
            "days_window":     days,
            "gender_filter":   gender,
            "category_filter": category,
        }).execute()
        return res.data or []
    except Exception:
        return []


def size_asymmetry(days: int = 30, gender: str | None = None,
                   min_stockouts: int = 20) -> list[dict]:
    """Return rows of (category, gender, asymmetry_score, total_stockouts,
    distinct_sizes, top_size, top_size_count) ordered by asymmetry desc."""
    sb = get_client()
    try:
        res = sb.rpc("dashboard_size_asymmetry", {
            "days_window":   days,
            "gender_filter": gender,
            "min_stockouts": min_stockouts,
            "min_sizes":     3,
        }).execute()
        return res.data or []
    except Exception:
        return []


def top_undersupply(days: int = 30, gender: str | None = None,
                    category: str | None = None, limit: int = 10) -> list[dict]:
    """Return top brand × category × size combinations by stockout count."""
    sb = get_client()
    try:
        res = sb.rpc("dashboard_top_undersupply", {
            "days_window":     days,
            "gender_filter":   gender,
            "category_filter": category,
            "result_limit":    limit,
        }).execute()
        return res.data or []
    except Exception:
        return []


def brand_pattern_coverage(category: str, gender: str | None,
                           top_size: str, days: int = 30) -> dict:
    """Return {brands_with_pattern, brands_in_category} for the Today's Read paragraph."""
    sb = get_client()
    try:
        res = sb.rpc("dashboard_brand_pattern_coverage", {
            "target_category": category,
            "target_gender":   gender,
            "target_top_size": top_size,
            "days_window":     days,
        }).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return {"brands_with_pattern": 0, "brands_in_category": 0}


# -------------------------------------------------------------------
# Today's Read paragraph generator
# -------------------------------------------------------------------

CATEGORY_DISPLAY = {
    "shirts":      "shirts",
    "t-shirts":    "t-shirts",
    "polos":       "polos",
    "sweatshirts": "sweatshirts",
    "hoodies":     "hoodies",
    "trousers":    "trousers",
    "jeans":       "jeans",
    "shorts":      "shorts",
    "jackets":     "jackets",
    "coats":       "coats",
    "blazers":     "blazers",
    "dresses":     "dresses",
    "skirts":      "skirts",
}


def _gender_phrase(gender: str | None) -> str:
    return {
        "men":    "men's",
        "women":  "women's",
        "unisex": "unisex",
        "kids":   "kids'",
    }.get((gender or "").lower(), "")


def generate_undersupply_read(days: int = 30, gender_filter: str | None = None) -> str:
    """Build the dynamic Today's Read paragraph for the under-supply tab.

    Template-based, no LLM. Slots are populated by querying the asymmetry index
    and the brand-pattern coverage. Falls back to a generic line if there's not
    enough data.
    """
    asym = size_asymmetry(days=days, gender=gender_filter, min_stockouts=20)
    if not asym:
        return ("Insufficient stockout volume in the last "
                f"{days} days to compute a reliable asymmetry signal. "
                "Try widening the time window, or check back tomorrow.")

    # Take the top asymmetric category
    top         = asym[0]
    cat         = top["category"]
    g           = top["gender"]
    cat_disp    = CATEGORY_DISPLAY.get(cat, cat)
    g_phrase    = _gender_phrase(g)
    top_size    = top["top_size"]
    top_count   = top["top_size_count"]
    total       = top["total_stockouts"]
    score       = float(top["asymmetry_score"])
    distinct    = top["distinct_sizes"]

    # Brand coverage check
    cov = brand_pattern_coverage(cat, g, top_size, days)
    brands_w_pattern = cov.get("brands_with_pattern", 0)
    brands_in_cat    = cov.get("brands_in_category", 0)

    coverage_clause = ""
    if brands_in_cat >= 2:
        coverage_clause = (
            f" The pattern holds across {brands_w_pattern} of {brands_in_cat} "
            f"brands selling in this category"
            + (" — strong cross-brand confirmation." if brands_w_pattern >= max(1, brands_in_cat - 1)
               else " — partial cross-brand confirmation.")
        )

    severity = ("Extreme" if score >= 1.0 else
                "Strong"  if score >= 0.7 else
                "Mild")

    leader_phrase = f"{g_phrase} {cat_disp}".strip()
    leader_phrase = leader_phrase[0].upper() + leader_phrase[1:]

    paragraph = (
        f"{leader_phrase} shows the strongest under-supply signal in the market right now "
        f"(asymmetry {score:.2f} — {severity}). Size {top_size} alone accounted for "
        f"{top_count} of {total} stockouts in the last {days} days across {distinct} "
        f"distinct sizes.{coverage_clause} "
        f"Production-side read: brands selling in this segment are consistently "
        f"underproducing size {top_size} relative to revealed demand."
    )
    return paragraph
