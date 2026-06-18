"""
Anomaly feed queries.

The homepage shows real-time anomalies fired by L1 signals. For v1, we draw
from three sources that already have live data:

  - L1·01 Genuine Price Drop      → price_events with significant drops
  - L1·08 Variant Stockout         → stockout_events during a discount
  - L1·12 New SKU Launch (clusters) → products.first_seen_at clusters

Each query returns a list of dicts ready to feed into the anomaly_card
component. They're filtered by the user's preferences (categories, watch list)
when those are set.
"""
from datetime import datetime, timedelta, timezone
from lib.db import get_client, safe_query


BRAND_DISPLAY = {
    "lc_waikiki": "LC Waikiki",
    "town_team":  "Town Team",
    "ravin":      "Ravin",
    "mens_club":  "Men's Club",
    "tree":       "Tree",
    "dott_jeans": "Dott Jeans",
    "defacto":    "DeFacto",
}


def _filter_by_user_prefs(rows: list, user: dict, brand_field: str = "brand") -> list:
    """Filter a result set by the user's category / watch list preferences.

    If the user has set no preferences, all rows pass through.
    """
    if not user:
        return rows
    watch = user.get("watch_list") or []
    if watch:
        rows = [r for r in rows if r.get(brand_field) in watch]
    return rows


def recent_significant_price_drops(hours: int = 24, min_pct: float = 15.0,
                                   user: dict = None) -> list:
    """Genuine Price Drops in the last N hours of at least min_pct depth."""
    sb = get_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = safe_query(
        sb.table("price_events")
        .select("id, brand, price_before, price_after, recorded_at, "
                "products!inner(name, category_normalized, gender)")
        .eq("direction", "down")
        .gte("recorded_at", since)
        .order("recorded_at", desc=True)
        .limit(40)
    )

    # Compute discount % and filter by threshold
    anomalies = []
    for r in rows:
        pb = float(r.get("price_before") or 0)
        pa = float(r.get("price_after") or 0)
        if pb <= 0 or pa <= 0 or pa >= pb:
            continue
        pct = round((pb - pa) / pb * 100, 1)
        if pct < min_pct:
            continue
        prod = r.get("products") or {}
        anomalies.append({
            "brand":        r.get("brand"),
            "brand_display": BRAND_DISPLAY.get(r.get("brand"), r.get("brand")),
            "product_name": prod.get("name", "Product"),
            "category":     prod.get("category_normalized", "uncategorized"),
            "gender":       prod.get("gender", ""),
            "price_before": pb,
            "price_after":  pa,
            "discount_pct": pct,
            "recorded_at":  r.get("recorded_at"),
        })

    return _filter_by_user_prefs(anomalies, user)[:15]


def recent_stockouts_during_discount(hours: int = 24, user: dict = None) -> list:
    """Variant Stockouts that occurred while the variant was on discount."""
    sb = get_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = safe_query(
        sb.table("stockout_events")
        .select("brand, size, color, price_at_event, discount_pct_at_event, recorded_at, "
                "products(name, category_normalized, gender)")
        .eq("event_type", "stockout")
        .eq("was_on_discount", True)
        .gte("recorded_at", since)
        .order("recorded_at", desc=True)
        .limit(20)
    )

    anomalies = []
    for r in rows:
        prod = r.get("products") or {}
        anomalies.append({
            "brand":         r.get("brand"),
            "brand_display": BRAND_DISPLAY.get(r.get("brand"), r.get("brand")),
            "product_name":  prod.get("name", "Product"),
            "size":          r.get("size"),
            "color":         r.get("color"),
            "category":      prod.get("category_normalized", "uncategorized"),
            "gender":        prod.get("gender", ""),
            "price":         float(r.get("price_at_event") or 0),
            "discount_pct":  float(r.get("discount_pct_at_event") or 0),
            "recorded_at":   r.get("recorded_at"),
        })

    return _filter_by_user_prefs(anomalies, user)[:10]


def recent_launch_clusters(days: int = 7, min_count: int = 5, user: dict = None) -> list:
    """Brands that launched many SKUs in a short window — collection drop signal."""
    sb = get_client()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = safe_query(
        sb.table("products")
        .select("brand, category_normalized, first_seen_at")
        .gte("first_seen_at", since)
        .order("first_seen_at", desc=True)
        .limit(500)
    )

    # Aggregate by brand + category
    buckets = {}
    for r in rows:
        b = r.get("brand")
        c = r.get("category_normalized", "uncategorized")
        key = (b, c)
        if key not in buckets:
            buckets[key] = {
                "brand":           b,
                "brand_display":   BRAND_DISPLAY.get(b, b),
                "category":        c,
                "count":           0,
                "latest_seen_at":  r.get("first_seen_at"),
            }
        buckets[key]["count"] += 1

    clusters = [b for b in buckets.values() if b["count"] >= min_count]
    clusters.sort(key=lambda x: x["count"], reverse=True)
    return _filter_by_user_prefs(clusters, user)[:5]


def assemble_anomaly_feed(user: dict = None) -> list:
    """Combine all anomaly sources into a single timeline, newest first.

    Each item is a dict the home view turns into an anomaly_card.
    """
    feed = []

    # Price drops
    for d in recent_significant_price_drops(hours=24, min_pct=15.0, user=user):
        feed.append({
            "severity": "opportunity" if d["discount_pct"] >= 30 else "noteworthy",
            "category": "Price",
            "title":    f"{d['brand_display']} \u00b7 {int(d['discount_pct'])}% drop on {d['category']}",
            "body":     f"{d['product_name'][:60]} \u2014 was {int(d['price_before'])} EGP, "
                        f"now {int(d['price_after'])} EGP. Genuine drop vs first-observed price.",
            "meta":     "L1\u00b701 Genuine Price Drop",
            "occurred_at": d["recorded_at"],
        })

    # Stockouts during discount (demand signal)
    for s in recent_stockouts_during_discount(hours=24, user=user):
        size_lbl = f"size {s['size']}" if s.get("size") else "variant"
        feed.append({
            "severity": "trend",
            "category": "Inventory",
            "title":    f"{s['brand_display']} \u00b7 {s['category']} {size_lbl} sold out during discount",
            "body":     f"{s['product_name'][:60]} \u2014 stocked out at "
                        f"{int(s['price'])} EGP ({int(s['discount_pct'])}% off). "
                        f"Demand response detected at this price point.",
            "meta":     "L1\u00b708 Variant Stockout (during discount)",
            "occurred_at": s["recorded_at"],
        })

    # Launch clusters
    for c in recent_launch_clusters(days=7, min_count=5, user=user):
        feed.append({
            "severity": "trend",
            "category": "Lifecycle",
            "title":    f"{c['brand_display']} \u00b7 {c['count']} new {c['category']} SKUs in the last 7 days",
            "body":     f"Cluster pattern indicates a collection drop or category expansion.",
            "meta":     "L1\u00b712 New SKU Launch (cluster)",
            "occurred_at": c["latest_seen_at"],
        })

    # Sort newest first
    feed.sort(key=lambda x: x.get("occurred_at") or "", reverse=True)
    return feed[:20]


def market_pulse_summary(user: dict = None) -> dict:
    """Fallback summary for when the anomaly feed is quiet.

    Returns counts of activity across the last 7 days so the home page
    is never empty.
    """
    sb = get_client()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    price_evt = safe_query(
        sb.table("price_events").select("id", count="exact")
        .gte("recorded_at", since).eq("direction", "down")
    )
    stockouts = safe_query(
        sb.table("stockout_events").select("id", count="exact")
        .eq("event_type", "stockout").gte("recorded_at", since)
    )
    launches = safe_query(
        sb.table("products").select("id", count="exact")
        .gte("first_seen_at", since)
    )

    return {
        "price_drops_7d": len(price_evt),
        "stockouts_7d":   len(stockouts),
        "launches_7d":    len(launches),
    }
