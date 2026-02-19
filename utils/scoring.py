"""
Scoring engine, metrics definitions, and classification for ChannelPRO™.

Contains the 29 scorecard metrics, score calculation, re-scoring,
partner classification (quadrant engine), break-even section defs,
and dynamic benchmark calculation via quintile analysis.
"""
import csv
import json
import math
import re

import pandas as pd
import streamlit as st

from utils.paths import csv_path, raw_path, save_path


# ── Helpers ─────────────────────────────────────────────────────────────

def _sf(val):
    """Coerce a display value to float, stripping $, %, commas, spaces."""
    if val is None:
        return None
    c = re.sub(r"[,$%\s]", "", str(val).strip())
    if c == "":
        return None
    try:
        return float(c)
    except ValueError:
        return None


# ── Scorecard metrics (29 metrics, 6 categories) ──────────────────────

SCORECARD_METRICS = [
    {"id":1,"key":"annual_revenues","name":"Annual revenues for vendor","explanation":"Total amount received from the partner, net of discounts/margins.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"50000"},"2":{"min":"50001","max":"150000"},"3":{"min":"150001","max":"350000"},"4":{"min":"350001","max":"750000"},"5":{"min":"750001","max":""}}},
    {"id":2,"key":"yoy_revenue_growth","name":"Year-on-year revenue growth","explanation":"% increase/decrease in revenues, past 12 mo over previous 12 mo.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"10"},"3":{"min":"10","max":"20"},"4":{"min":"20","max":"35"},"5":{"min":"35","max":""}}},
    {"id":3,"key":"net_new_logo_revenues","name":"Net-new logo revenues","explanation":"Revenues from selling to new customers.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"10000"},"2":{"min":"10001","max":"50000"},"3":{"min":"50001","max":"150000"},"4":{"min":"150001","max":"350000"},"5":{"min":"350001","max":""}}},
    {"id":4,"key":"pct_revenues_saas","name":"% of vendor revenues from SaaS","explanation":"Transformation to SaaS/recurring revenues.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":5,"key":"net_revenue_expansion","name":"Net revenue expansion","explanation":"Growth in revenues for existing customers.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"5"},"3":{"min":"5","max":"15"},"4":{"min":"15","max":"25"},"5":{"min":"25","max":""}}},
    {"id":6,"key":"total_revenues","name":"Total revenues (if available)","explanation":"Overall revenues including all products and services.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"1000000"},"2":{"min":"1000001","max":"5000000"},"3":{"min":"5000001","max":"20000000"},"4":{"min":"20000001","max":"100000000"},"5":{"min":"100000001","max":""}}},
    {"id":7,"key":"avg_deal_size_net_new","name":"Average deal size – net-new logos","explanation":"Average annualized subscription/license value for new customers.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5000"},"2":{"min":"5001","max":"15000"},"3":{"min":"15001","max":"40000"},"4":{"min":"40001","max":"100000"},"5":{"min":"100001","max":""}}},
    {"id":8,"key":"avg_deal_size_renewals","name":"Average deal size – renewals","explanation":"Average annualized subscription/license value for renewal customers.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5000"},"2":{"min":"5001","max":"15000"},"3":{"min":"15001","max":"40000"},"4":{"min":"40001","max":"100000"},"5":{"min":"100001","max":""}}},
    {"id":9,"key":"avg_time_to_close","name":"Average time to close – net new logos","explanation":"Deal registration to signed subscription/EULA for new customers.","type":"quantitative","unit":"days","direction":"lower_is_better","cat":"Sales Performance","defaults":{"1":{"min":"181","max":""},"2":{"min":"121","max":"180"},"3":{"min":"61","max":"120"},"4":{"min":"31","max":"60"},"5":{"min":"0","max":"30"}}},
    {"id":10,"key":"registered_deals","name":"Registered deals","explanation":"Number of deals registered with vendor.","type":"quantitative","unit":"count","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"6","max":"15"},"3":{"min":"16","max":"30"},"4":{"min":"31","max":"60"},"5":{"min":"61","max":""}}},
    {"id":11,"key":"win_loss_ratio","name":"Win/loss ratio","explanation":"% of registered deals that closed.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"40"},"4":{"min":"40","max":"60"},"5":{"min":"60","max":"100"}}},
    {"id":12,"key":"partner_generated_opps_pct","name":"Partner Generated Opps as % of Pipeline","explanation":"Partner-generated vs. vendor leads.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"50"},"4":{"min":"50","max":"75"},"5":{"min":"75","max":"100"}}},
    {"id":13,"key":"frequency_of_business","name":"Frequency of business","explanation":"Steady flow or seasonal?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":"Sporadic — 1-2 transactions/year","2":"Seasonal — clustered in 1-2 quarters","3":"Moderate — activity most quarters","4":"Consistent — monthly or near-monthly","5":"Highly active — continuous deal flow"}},
    {"id":14,"key":"renewal_rate","name":"Renewal rate","explanation":"% of subscriptions renewed.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":{"min":"0","max":"60"},"2":{"min":"60","max":"75"},"3":{"min":"75","max":"85"},"4":{"min":"85","max":"93"},"5":{"min":"93","max":"100"}}},
    {"id":15,"key":"customer_satisfaction","name":"Customer satisfaction","explanation":"NPS or satisfaction measurement.","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"No measurement; frequent complaints","2":"Anecdotal only; some dissatisfaction","3":"Measured informally; average","4":"Formal NPS/CSAT; consistently positive","5":"Industry-leading; referenceable customers"}},
    {"id":16,"key":"communication_with_vendor","name":"Communication with vendor","explanation":"Quality of communications — calls, QBRs, visits.","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"Unresponsive — hard to reach","2":"Reactive only","3":"Periodic — monthly calls, no QBR","4":"Strong — regular cadence, QBRs","5":"Exemplary — weekly touchpoints, exec visits"}},
    {"id":17,"key":"mdf_utilization_rate","name":"MDF utilization rate","explanation":"Using vendor-sponsored marketing funds?","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":18,"key":"quality_of_sales_org","name":"Quality of sales organization","explanation":"Do they need more guidance?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Weak — no dedicated reps","2":"Below average — lack product knowledge","3":"Adequate — average metrics","4":"Strong — good pipeline management","5":"Excellent — top-tier, consistently high"}},
    {"id":19,"key":"vendor_certifications","name":"Vendor certification(s)","explanation":"Investing in your technology?","type":"quantitative","unit":"certs","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"0"},"2":{"min":"1","max":"2"},"3":{"min":"3","max":"5"},"4":{"min":"6","max":"10"},"5":{"min":"11","max":""}}},
    {"id":20,"key":"sales_support_calls","name":"Sales support calls received","explanation":"Big pipeline or can't sell?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive — lack of knowledge","2":"Frequent routine questions","3":"Moderate — mixed","4":"Mostly deal-strategy-driven","5":"Rare — complex high-value only"}},
    {"id":21,"key":"tech_support_calls","name":"Tech support calls received","explanation":"Lack of training?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive — training gaps","2":"Frequent — certs should cover","3":"Average — occasional escalations","4":"Low — complex edge cases","5":"Minimal — self-sufficient"}},
    {"id":22,"key":"dedication_vs_competitive","name":"Dedication vs. competitive products","explanation":"Strategic vendor or afterthought?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Sells competitor as primary","2":"Competitor default; you by request","3":"Sells both equally","4":"You preferred; competitor secondary","5":"Exclusively sells your solution"}},
    {"id":23,"key":"dedication_vs_other_vendors","name":"Dedication vs. other vendors","explanation":"% of business your solution represents.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"5","max":"15"},"3":{"min":"15","max":"30"},"4":{"min":"30","max":"50"},"5":{"min":"50","max":"100"}}},
    {"id":24,"key":"geographical_coverage","name":"Geographical market coverage","explanation":"Right-sized territory?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Very limited local presence","2":"Small territory; gaps","3":"Adequate regional coverage","4":"Strong multi-region, aligned","5":"National/intl or dominant"}},
    {"id":25,"key":"vertical_coverage","name":"Vertical market coverage","explanation":"Specialize in verticals?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"No vertical focus","2":"Emerging in 1 vertical","3":"Established in 1-2 verticals","4":"Strong domain expertise","5":"Dominant authority; deep base"}},
    {"id":26,"key":"quality_of_management","name":"Quality of management","explanation":"How well do they run their business?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Poor — disorganized","2":"Below avg — reactive","3":"Adequate — competent","4":"Strong — proactive, clear strategy","5":"Exceptional — visionary leadership"}},
    {"id":27,"key":"known_litigation","name":"Known litigation (No=5, Yes=1)","explanation":"Involved in lawsuits?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Active major litigation","2":"Material financial exposure","3":"Minor pending disputes","4":"Past litigation resolved","5":"No known litigation"}},
    {"id":28,"key":"export_control_ip","name":"Export control & IP protection","explanation":"Complying with provisions?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Known violations","2":"Gaps; no remediation","3":"Generally compliant","4":"Fully compliant; proactive","5":"Best-in-class compliance"}},
    {"id":29,"key":"financial_strength","name":"Financial strength","explanation":"Cash-flow struggles or strong margins?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Severe cash-flow issues","2":"Thin margins; credit concerns","3":"Stable but modest","4":"Healthy margins; consistent profit","5":"Very strong; well-capitalized"}},
]

CATEGORIES = [
    {"label": "Revenue & Growth", "icon": "💰", "keys": ["annual_revenues", "yoy_revenue_growth", "net_new_logo_revenues", "pct_revenues_saas", "net_revenue_expansion", "total_revenues"]},
    {"label": "Sales Performance", "icon": "📈", "keys": ["avg_deal_size_net_new", "avg_deal_size_renewals", "avg_time_to_close", "registered_deals", "win_loss_ratio", "partner_generated_opps_pct", "frequency_of_business"]},
    {"label": "Retention & Satisfaction", "icon": "🤝", "keys": ["renewal_rate", "customer_satisfaction", "communication_with_vendor"]},
    {"label": "Enablement & Support", "icon": "🎓", "keys": ["mdf_utilization_rate", "quality_of_sales_org", "vendor_certifications", "sales_support_calls", "tech_support_calls"]},
    {"label": "Strategic Fit", "icon": "🧭", "keys": ["dedication_vs_competitive", "dedication_vs_other_vendors", "geographical_coverage", "vertical_coverage"]},
    {"label": "Risk & Governance", "icon": "🛡️", "keys": ["quality_of_management", "known_litigation", "export_control_ip", "financial_strength"]},
]

METRICS_BY_KEY = {m["key"]: m for m in SCORECARD_METRICS}

# Score → colour mapping
SC = {1: "#dc4040", 2: "#e8820c", 3: "#d4a917", 4: "#49a34f", 5: "#1b6e23"}

# Metric-name aliases used by the classification engine
METRIC_ALIASES: dict[str, str | None] = {
    "total company revenues": "total_revenues",
    "annual vendor revenues": "annual_revenues",
    "annual revenues": "annual_revenues",
    "y-y growth rate": "yoy_revenue_growth",
    "y-y revenue growth": "yoy_revenue_growth",
    "year-on-year revenue growth": "yoy_revenue_growth",
    "net new logo growth": "net_new_logo_revenues",
    "net-new logo revenues": "net_new_logo_revenues",
    "# of known competitors": None,
    "your product ranking": None,
    "average deal size": "avg_deal_size_net_new",
    "average time to close": "avg_time_to_close",
}
for _m in SCORECARD_METRICS:
    METRIC_ALIASES[_m["key"]] = _m["key"]
    METRIC_ALIASES[_m["name"].lower()] = _m["key"]


# ── Scoring ─────────────────────────────────────────────────────────────

def calc_score(mk: str, val, criteria: dict | None = None) -> int | None:
    """Score a single metric value (1-5) against the criteria ranges/descriptors."""
    cr = (criteria or st.session_state.get("criteria", {})).get(mk)
    if not cr or not cr.get("enabled", True):
        return None
    if cr["type"] == "quantitative":
        v = _sf(val)
        if v is None:
            return None
        for s in ("5", "4", "3", "2", "1"):
            r = cr["ranges"][s]
            lo, hi = _sf(r["min"]), _sf(r["max"])
            if lo is not None and hi is not None and lo <= v <= hi:
                return int(s)
            if lo is not None and hi is None and v >= lo:
                return int(s)
            if lo is None and hi is not None and v <= hi:
                return int(s)
        return 1
    else:
        if not val or val == "— Select —":
            return None
        for s in ("1", "2", "3", "4", "5"):
            if cr["descriptors"][s] == val:
                return int(s)
        return None


def enabled(criteria: dict | None = None) -> list[dict]:
    """Return the list of enabled SCORECARD_METRICS."""
    cr = criteria or st.session_state.get("criteria", {})
    return [m for m in SCORECARD_METRICS if cr.get(m["key"], {}).get("enabled", True)]


def grade(pct: float) -> tuple[str, str]:
    """Map a percentage score to a letter grade and colour hex."""
    if pct >= 90:
        return "A", "#1b6e23"
    if pct >= 80:
        return "B+", "#49a34f"
    if pct >= 70:
        return "B", "#6aab2e"
    if pct >= 60:
        return "C+", "#d4a917"
    if pct >= 50:
        return "C", "#e8820c"
    return "D", "#dc4040"


def tiers() -> list[str]:
    """Return the configured partner tier labels."""
    raw = st.session_state.get("client_info", {}).get("partner_designations", "")
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []


def synthetic_raw_for_score(mk: str, score: int, cr: dict | None = None):
    """Given a metric key and desired score (1-5), return a raw value that
    ``calc_score`` would map to that score."""
    if score is None or score == 0:
        return None
    criteria = cr or st.session_state.get("criteria", {})
    mc = criteria.get(mk)
    if not mc:
        return str(score)
    if mc["type"] == "qualitative":
        return mc.get("descriptors", {}).get(str(score), "")
    else:
        r = mc.get("ranges", {}).get(str(score), {})
        lo, hi = _sf(r.get("min")), _sf(r.get("max"))
        if lo is not None and hi is not None:
            return str((lo + hi) / 2)
        elif lo is not None:
            return str(lo + 1)
        elif hi is not None:
            return str(hi)
        return str(score)


# ── Criteria init / migration ──────────────────────────────────────────

def init_criteria() -> None:
    """Initialise scoring criteria in session state, migrating if needed."""
    if "criteria" in st.session_state:
        cr = st.session_state["criteria"]
        changed = False
        for m in SCORECARD_METRICS:
            k = m["key"]
            if k not in cr:
                if m["type"] == "quantitative":
                    cr[k] = {
                        "name": m["name"], "type": "quantitative", "unit": m["unit"],
                        "direction": m["direction"], "enabled": True,
                        "ranges": {s: {"min": m["defaults"][s]["min"], "max": m["defaults"][s]["max"]} for s in ("1", "2", "3", "4", "5")},
                    }
                else:
                    cr[k] = {
                        "name": m["name"], "type": "qualitative", "unit": None,
                        "direction": m["direction"], "enabled": True,
                        "descriptors": {s: m["defaults"][s] for s in ("1", "2", "3", "4", "5")},
                    }
                changed = True
        if changed:
            st.session_state["criteria"] = cr
        # Ensure criteria file exists on disk (covers sessions that
        # initialised before the file-write logic was added).
        sp = save_path()
        if not sp.exists():
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_text(json.dumps(cr, indent=2))
        return

    sp = save_path()
    if sp.exists():
        try:
            cr = json.loads(sp.read_text())
            st.session_state["criteria"] = cr
            init_criteria()  # run migration on loaded data
            return
        except Exception:
            pass

    cr = {}
    for m in SCORECARD_METRICS:
        k = m["key"]
        if m["type"] == "quantitative":
            cr[k] = {
                "name": m["name"], "type": "quantitative", "unit": m["unit"],
                "direction": m["direction"], "enabled": True,
                "ranges": {s: {"min": m["defaults"][s]["min"], "max": m["defaults"][s]["max"]} for s in ("1", "2", "3", "4", "5")},
            }
        else:
            cr[k] = {
                "name": m["name"], "type": "qualitative", "unit": None,
                "direction": m["direction"], "enabled": True,
                "descriptors": {s: m["defaults"][s] for s in ("1", "2", "3", "4", "5")},
            }
    st.session_state["criteria"] = cr
    # Persist defaults to disk so pages that gate on the file can proceed
    sp = save_path()
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(cr, indent=2))


def ensure_criteria_complete() -> None:
    """Ensure all SCORECARD_METRICS keys exist in session criteria (migration helper)."""
    cr = st.session_state.get("criteria", {})
    for m in SCORECARD_METRICS:
        k = m["key"]
        if k not in cr:
            if m["type"] == "quantitative":
                cr[k] = {
                    "name": m["name"], "type": "quantitative", "unit": m["unit"],
                    "direction": m["direction"], "enabled": True,
                    "ranges": {s: {"min": m["defaults"][s]["min"], "max": m["defaults"][s]["max"]} for s in ("1", "2", "3", "4", "5")},
                }
            else:
                cr[k] = {
                    "name": m["name"], "type": "qualitative", "unit": None,
                    "direction": m["direction"], "enabled": True,
                    "descriptors": {s: m["defaults"][s] for s in ("1", "2", "3", "4", "5")},
                }
    st.session_state["criteria"] = cr


def save_criteria() -> None:
    """Persist criteria from session state to disk, then re-score all partners."""
    cr = st.session_state["criteria"]
    ensure_criteria_complete()
    for m in SCORECARD_METRICS:
        mk = m["key"]
        if mk not in cr:
            continue
        en_key = f"p1_{mk}_en"
        if en_key in st.session_state:
            cr[mk]["enabled"] = st.session_state[en_key]
        if m["type"] == "quantitative":
            for s in ("1", "2", "3", "4", "5"):
                min_key = f"p1_{mk}_s{s}_min"
                max_key = f"p1_{mk}_s{s}_max"
                if min_key in st.session_state:
                    cr[mk]["ranges"][s]["min"] = st.session_state[min_key]
                if max_key in st.session_state:
                    cr[mk]["ranges"][s]["max"] = st.session_state[max_key]
        else:
            for s in ("1", "2", "3", "4", "5"):
                desc_key = f"p1_{mk}_s{s}_desc"
                if desc_key in st.session_state:
                    cr[mk]["descriptors"][s] = st.session_state[desc_key]
    save_path().write_text(json.dumps(cr, indent=2))
    rescore_all()


# ── Re-scoring ──────────────────────────────────────────────────────────

def rescore_all() -> None:
    """Re-score all partners using current criteria and rewrite CSV."""
    from utils.data import invalidate_partner_cache

    rp = raw_path()
    if not rp.exists():
        return
    try:
        raw_partners = json.loads(rp.read_text())
    except Exception:
        return
    if not raw_partners:
        return
    cr = st.session_state.get("criteria")
    if not cr:
        return
    em = enabled(cr)
    fnames = [
        "partner_name", "partner_year", "partner_tier", "partner_discount",
        "partner_city", "partner_country", "pam_name", "pam_email",
    ]
    fnames += [m["key"] for m in em]
    fnames += ["total_score", "max_possible", "percentage"]
    cp = csv_path()
    with open(cp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
        w.writeheader()
        for rp_item in raw_partners:
            row = {
                k: rp_item.get(k, "")
                for k in [
                    "partner_name", "partner_year", "partner_tier", "partner_discount",
                    "partner_city", "partner_country", "pam_name", "pam_email",
                ]
            }
            si = {}
            for m in em:
                mk = m["key"]
                raw_val = rp_item.get(f"raw_{mk}")
                scr = calc_score(mk, raw_val, cr) if raw_val else None
                row[mk] = scr if scr else ""
                if scr:
                    si[mk] = scr
            total = sum(si.values())
            sn = len(si)
            mp = sn * 5
            row["total_score"] = total
            row["max_possible"] = mp
            row["percentage"] = round(total / mp * 100, 1) if mp else 0
            w.writerow(row)
    invalidate_partner_cache()


# ── Dynamic benchmark calculation (quintile-based) ────────────────────


def calculate_dynamic_ranges(
    df: pd.DataFrame,
    criteria: dict | None = None,
) -> dict:
    """Compute quintile-based 1–5 scoring ranges from partner data.

    For each **quantitative** metric that is enabled in *criteria*:
    - Extract the raw values from *df* (columns named ``raw_<key>``).
    - Drop nulls / non-numeric values.
    - If all remaining values are identical (zero variance), assign score 3
      to that exact value and spread ±1 around it.
    - Otherwise use ``pandas.qcut`` with 5 equal-frequency bins.
    - Respect ``direction``: *higher_is_better* → ascending bins 1→5;
      *lower_is_better* → reversed bins 5→1.

    Qualitative metrics are left unchanged.

    Returns a **new** criteria dict (same shape as the persisted
    ``scoring_criteria.json``) with updated ``ranges`` for quantitative
    metrics.
    """
    cr = {k: dict(v) for k, v in (criteria or st.session_state.get("criteria", {})).items()}
    if not cr:
        return cr

    em = enabled(cr)
    for m in em:
        mk = m["key"]
        if m["type"] != "quantitative":
            continue
        mc = cr.get(mk)
        if not mc:
            continue

        col = f"raw_{mk}"
        if col not in df.columns:
            continue

        # Extract numeric values, dropping NaN / non-parseable
        raw = df[col].apply(_sf)
        vals = raw.dropna()
        if vals.empty:
            continue

        unique = vals.nunique()
        is_lower = m["direction"] == "lower_is_better"

        if unique == 1:
            # Zero-variance edge case — all partners share the same value.
            # Build 6 boundaries (5 bins) centred on the single value.
            v = vals.iloc[0]
            spread = max(abs(v) * 0.1, 1)  # ±10% or ±1
            boundaries = [
                v - 2 * spread,
                v - spread,
                v - spread / 2,
                v + spread / 2,
                v + spread,
                v + 2 * spread,
            ]
        else:
            # Use qcut to find quintile boundaries.
            # duplicates="drop" handles repeated values on bin edges.
            try:
                _, bin_edges = pd.qcut(vals, 5, retbins=True, duplicates="drop")
            except ValueError:
                continue

            edges = list(bin_edges)
            # qcut may return fewer than 6 edges when many duplicates exist.
            # Pad to ensure we always have 6 boundaries (5 bins).
            while len(edges) < 6:
                edges.append(edges[-1])
            boundaries = edges  # [min, q20, q40, q60, q80, max]

        # Build the five score-range dicts.
        # For higher_is_better: score 1 = lowest quintile → score 5 = highest
        # For lower_is_better:  score 1 = highest quintile → score 5 = lowest
        ranges: dict[str, dict[str, str]] = {}
        for score_idx in range(5):  # 0..4 → scores 1..5
            lo = boundaries[score_idx]
            hi = boundaries[score_idx + 1]
            lo_r = math.floor(lo * 100) / 100  # round down
            hi_r = math.ceil(hi * 100) / 100   # round up

            if is_lower:
                # Reverse: bin 0 (lowest values) = score 5
                score_label = str(5 - score_idx)
            else:
                score_label = str(score_idx + 1)

            # First bin has no lower bound cap; last bin has no upper cap
            if score_idx == 0:
                ranges[score_label] = {"min": "", "max": _fmt(hi_r, m)}
            elif score_idx == 4:
                ranges[score_label] = {"min": _fmt(lo_r, m), "max": ""}
            else:
                ranges[score_label] = {"min": _fmt(lo_r, m), "max": _fmt(hi_r, m)}

        mc["ranges"] = ranges
        cr[mk] = mc

    return cr


def _fmt(val: float, metric: dict) -> str:
    """Format a boundary value for storage — integers where appropriate."""
    if val == int(val):
        return str(int(val))
    if metric.get("unit") in ("$", "count", "certs", "days"):
        return str(int(round(val)))
    return str(round(val, 2))


def recalculate_benchmarks() -> dict:
    """Load the active tenant's raw partner data, compute dynamic quintile
    ranges for all quantitative metrics, persist the updated criteria, and
    re-score every partner.

    Returns a summary dict ``{"updated": [list of metric names], "skipped": [...]}``.
    """
    from utils.data import load_raw

    raw_list = load_raw()
    if not raw_list:
        return {"updated": [], "skipped": ["No partner data found"]}

    df = pd.DataFrame(raw_list)
    cr = st.session_state.get("criteria")
    if not cr:
        return {"updated": [], "skipped": ["No scoring criteria loaded"]}

    new_cr = calculate_dynamic_ranges(df, cr)

    # Identify which metrics actually changed
    updated_names: list[str] = []
    skipped_names: list[str] = []
    for m in SCORECARD_METRICS:
        mk = m["key"]
        if m["type"] != "quantitative":
            continue
        old_ranges = cr.get(mk, {}).get("ranges")
        new_ranges = new_cr.get(mk, {}).get("ranges")
        if old_ranges and new_ranges and old_ranges != new_ranges:
            updated_names.append(m["name"])
        elif not new_ranges or old_ranges == new_ranges:
            skipped_names.append(m["name"])

    # Persist
    st.session_state["criteria"] = new_cr
    save_path().write_text(json.dumps(new_cr, indent=2))
    rescore_all()

    return {"updated": updated_names, "skipped": skipped_names}


# ── Revenue Recovery Calculator ───────────────────────────────────────


def calculate_revenue_recovery(
    raw_partners: list[dict],
    net_new_threshold: float,
    baseline_margin_pct: float = 10.0,
) -> pd.DataFrame:
    """Identify non-performing longtail partners and calculate margin recapture.

    A partner is a *non-performer* when their raw net-new logo revenue is
    below *net_new_threshold*.

    For each non-performer the function computes:
    - Current margin cost  = annual_revenue * current_margin%
    - Proposed margin cost = annual_revenue * baseline_margin%
    - Recapture            = current - proposed

    Returns a DataFrame sorted by annual revenue descending.  Columns:
        Partner, Annual Revenue, Current Margin %, Current Margin $,
        New Margin %, New Margin $, Recapture $, Net-New Logo Revenue
    """
    rows: list[dict] = []
    for rp in raw_partners:
        # Parse net-new logo revenue
        nn_val = _sf(rp.get("raw_net_new_logo_revenues"))
        if nn_val is None:
            nn_val = 0.0
        if nn_val >= net_new_threshold:
            continue  # performing partner — skip

        # Parse annual revenue (try raw first, fall back to total)
        rev = _sf(rp.get("raw_annual_revenues"))
        if rev is None:
            rev = _sf(rp.get("raw_total_revenues"))
        if rev is None or rev <= 0:
            continue

        # Parse current margin from partner_discount field
        margin_pct = _sf(rp.get("partner_discount"))
        if margin_pct is None or margin_pct <= 0:
            continue

        current_cost = rev * margin_pct / 100.0
        proposed_cost = rev * baseline_margin_pct / 100.0
        recapture = current_cost - proposed_cost

        rows.append({
            "Partner": rp.get("partner_name", "Unknown"),
            "Annual Revenue": rev,
            "Current Margin %": margin_pct,
            "Current Margin $": current_cost,
            "New Margin %": baseline_margin_pct,
            "New Margin $": proposed_cost,
            "Recapture $": recapture,
            "Net-New Logo Revenue": nn_val,
        })

    if not rows:
        return pd.DataFrame(columns=[
            "Partner", "Annual Revenue", "Current Margin %",
            "Current Margin $", "New Margin %", "New Margin $",
            "Recapture $", "Net-New Logo Revenue",
        ])

    df = pd.DataFrame(rows)
    df.sort_values("Annual Revenue", ascending=False, inplace=True, ignore_index=True)
    return df


# ── Classification engine (quadrants) ──────────────────────────────────

DEFAULT_Q_CONFIG = {
    1: [("total_revenues", "high"), ("annual_revenues", "low"), ("yoy_revenue_growth", "low")],
    2: [("annual_revenues", "high"), ("yoy_revenue_growth", "high"), ("net_new_logo_revenues", "high")],
    3: [("annual_revenues", "high"), ("yoy_revenue_growth", "low"), ("net_new_logo_revenues", "mid")],
}

Q_LABELS = {
    1: ("Strategic / Underperforming", "#2563eb"),
    2: ("Top Performers", "#1b6e23"),
    3: ("Growth Potential", "#d4a917"),
    4: ("Long Tail", "#dc4040"),
}

Q_DESCS = {
    1: "High total revenue but low vendor-specific performance",
    2: "Strong across revenue, growth, and new logos",
    3: "Good revenue but stagnant growth",
    4: "Does not meet criteria for quadrants 1\u20133",
}


def _level_match(sv, level) -> bool:
    try:
        v = int(sv)
    except (TypeError, ValueError):
        return False
    if v == 0:
        return False
    if level is None or level == "any":
        return v > 0
    if level == "high":
        return v >= 4
    if level == "mid":
        return v == 3
    if level == "low":
        return v <= 2
    return False


def classify_partners(partners: list[dict], qconfig: dict, em_keys: set) -> dict:
    """Assign each partner to a quadrant (1-3) or Long Tail (4)."""
    results = {}
    for p in partners:
        name = p.get("partner_name", "Unknown")
        try:
            total = int(p.get("total_score", 0) or 0)
        except (TypeError, ValueError):
            total = 0
        if total == 0:
            continue
        assigned = None
        for qn in sorted(qconfig.keys()):
            crit = qconfig[qn]
            match = True
            for mk, lvl in crit:
                if mk is None or mk not in em_keys:
                    continue
                if not _level_match(p.get(mk), lvl):
                    match = False
                    break
            if match and crit:
                assigned = qn
                break
        results[name] = assigned if assigned is not None else 4
    return results


# ── Break-even section definitions ─────────────────────────────────────

BE_SECTIONS = [
    {"section": "Personnel and Overhead", "items": [
        "Partner managers - salaries and commissions", "Social charges", "Office space",
        "Phone, laptop, software", "Admin and order processing", "Overhead allocation"]},
    {"section": "Infrastructure and Technology", "items": [
        "PRM and other software used for the channel", "Integration with partner systems",
        "Security for data sharing and privacy regulations"]},
    {"section": "Marketing and Promotion", "items": [
        "Co-marketing and MDF", "SEO and other campaigns", "Marketing collateral",
        "Website maintenance", "Incentives - spiffs, rebates, sales contests", "Events and conferences"]},
    {"section": "Technical and Sales Support", "items": [
        "Technical support salaries", "Pre-sales support salaries", "Social charges",
        "Office space", "Phone, laptop, software", "Overhead allocation"]},
    {"section": "Training and Certification", "items": [
        "Product training", "Sales training", "Certification programs"]},
    {"section": "Legal and Compliance", "items": [
        "Contracts", "Compliance", "Conflict resolution - contract disputes and mediation"]},
    {"section": "Travel and Meetings", "items": [
        "Face-to-face meetings", "Joint sales calls"]},
    {"section": "Performance Metrics and Reporting", "items": [
        "Partner performance tools salary", "Reporting"]},
    {"section": "Scaling and Expansion", "items": [
        "Partner recruitment manager", "Social charges", "Office space", "Overhead allocation",
        "Phone, laptop, software", "Partner recruitment marketing", "Travel and meetings", "Onboarding costs"]},
]

BE_SECTION_ICONS = {
    "Personnel and Overhead": "👥",
    "Infrastructure and Technology": "🖥️",
    "Marketing and Promotion": "📣",
    "Technical and Sales Support": "🛠️",
    "Training and Certification": "🎓",
    "Legal and Compliance": "⚖️",
    "Travel and Meetings": "✈️",
    "Performance Metrics and Reporting": "📊",
    "Scaling and Expansion": "🚀",
}
