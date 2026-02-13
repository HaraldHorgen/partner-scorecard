"""
Partner Scorecard — Phase 1 + Phase 2
======================================
Phase 1: Define 1-5 scoring criteria for all 28 metrics.
Phase 2: Enter partner performance, auto-calculate scores,
         display results table with total & percentage (out of 140 max).

Run:  streamlit run app.py
"""

import json, math, pathlib, re
import streamlit as st

# ═════════════════════════════════════════════════════════════════════════
# 0.  METRIC DEFINITIONS
# ═════════════════════════════════════════════════════════════════════════

SCORECARD_METRICS: list[dict] = [
    {"id":1,"key":"annual_revenues","name":"Annual revenues for vendor","explanation":"Total amount received from the partner, net of discounts/margins. Past 12 months or last fiscal year.","type":"quantitative","format":"currency_range","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"50000"},"2":{"min":"50001","max":"150000"},"3":{"min":"150001","max":"350000"},"4":{"min":"350001","max":"750000"},"5":{"min":"750001","max":""}}},
    {"id":2,"key":"yoy_revenue_growth","name":"Year-on-year revenue growth","explanation":"Percentage increase/decrease in revenues, past 12 months over previous 12 months.","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"10"},"3":{"min":"10","max":"20"},"4":{"min":"20","max":"35"},"5":{"min":"35","max":""}}},
    {"id":3,"key":"net_new_logo_revenues","name":"Net-new logo revenues","explanation":"Revenues from selling to new customers over the past 12 months.","type":"quantitative","format":"currency_range","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"10000"},"2":{"min":"10001","max":"50000"},"3":{"min":"50001","max":"150000"},"4":{"min":"150001","max":"350000"},"5":{"min":"350001","max":""}}},
    {"id":4,"key":"pct_revenues_saas","name":"Percentage of vendor revenues from SaaS","explanation":"How successful the partner has been transforming to SaaS/recurring revenues.","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":5,"key":"net_revenue_expansion","name":"Net revenue expansion","explanation":"Growth in revenues for existing customers (negative churn).","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"5"},"3":{"min":"5","max":"15"},"4":{"min":"15","max":"25"},"5":{"min":"25","max":""}}},
    {"id":6,"key":"total_revenues","name":"Total revenues (if available)","explanation":"Overall revenues for the partner including all products and services.","type":"quantitative","format":"currency_range","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"1000000"},"2":{"min":"1000001","max":"5000000"},"3":{"min":"5000001","max":"20000000"},"4":{"min":"20000001","max":"100000000"},"5":{"min":"100000001","max":""}}},
    {"id":7,"key":"average_deal_size","name":"Average deal size","explanation":"Average annualized subscription/license value. Excludes services, maintenance.","type":"quantitative","format":"currency_range","unit":"$","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5000"},"2":{"min":"5001","max":"15000"},"3":{"min":"15001","max":"40000"},"4":{"min":"40001","max":"100000"},"5":{"min":"100001","max":""}}},
    {"id":8,"key":"avg_time_to_close","name":"Average time to close","explanation":"Time from deal registration to signed subscription/EULA. Excludes payment cycle.","type":"quantitative","format":"number_range","unit":"days","direction":"lower_is_better","cat":"Sales Performance","defaults":{"1":{"min":"181","max":""},"2":{"min":"121","max":"180"},"3":{"min":"61","max":"120"},"4":{"min":"31","max":"60"},"5":{"min":"0","max":"30"}}},
    {"id":9,"key":"registered_deals","name":"Registered deals","explanation":"Number of deals partner registered with vendor.","type":"quantitative","format":"number_range","unit":"count","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"6","max":"15"},"3":{"min":"16","max":"30"},"4":{"min":"31","max":"60"},"5":{"min":"61","max":""}}},
    {"id":10,"key":"win_loss_ratio","name":"Win/loss ratio for registered deals","explanation":"Percentage of registered deals from partner that closed.","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"40"},"4":{"min":"40","max":"60"},"5":{"min":"60","max":"100"}}},
    {"id":11,"key":"partner_generated_opps_pct","name":"Partner Generated Opps as % of Pipeline","explanation":"Opportunities the partner generated vs. leads the vendor sent them.","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"50"},"4":{"min":"50","max":"75"},"5":{"min":"75","max":"100"}}},
    {"id":12,"key":"frequency_of_business","name":"Frequency of business","explanation":"How many transactions in a 12-month period — steady flow or seasonal?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":"Sporadic — 1-2 transactions/year, large gaps","2":"Seasonal — clustered in 1-2 quarters","3":"Moderate — activity most quarters, some gaps","4":"Consistent — monthly or near-monthly transactions","5":"Highly active — continuous deal flow year-round"}},
    {"id":13,"key":"renewal_rate","name":"Renewal rate","explanation":"Percentage of subscriptions renewed during the past 12 months.","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":{"min":"0","max":"60"},"2":{"min":"60","max":"75"},"3":{"min":"75","max":"85"},"4":{"min":"85","max":"93"},"5":{"min":"93","max":"100"}}},
    {"id":14,"key":"customer_satisfaction","name":"Customer satisfaction","explanation":"Do you or the partner measure customer satisfaction, e.g., NPS score?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"No measurement; frequent complaints/escalations","2":"Anecdotal only; some known dissatisfaction","3":"Measured informally; average satisfaction","4":"Formal NPS/CSAT in place; consistently positive","5":"Industry-leading scores; referenceable customers"}},
    {"id":15,"key":"communication_with_vendor","name":"Communication with vendor","explanation":"Quality of communications — regular calls, QBRs, mutual visits.","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"Unresponsive — no regular cadence, hard to reach","2":"Reactive only — responds when contacted","3":"Periodic — monthly calls but no formal QBR","4":"Strong — regular cadence, QBRs, occasional visits","5":"Exemplary — weekly touchpoints, QBRs, exec visits"}},
    {"id":16,"key":"mdf_utilization_rate","name":"MDF utilization rate","explanation":"Are they making use of vendor-sponsored marketing funds?","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":17,"key":"quality_of_sales_org","name":"Quality of sales organization","explanation":"Tied to deal size, time to close, win/loss ratio. Do they need more guidance?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Weak — no dedicated reps, no pipeline discipline","2":"Below average — reps lack product knowledge","3":"Adequate — competent team, average metrics","4":"Strong — skilled reps, good pipeline management","5":"Excellent — top-tier team, consistently high metrics"}},
    {"id":18,"key":"vendor_certifications","name":"Vendor certification(s)","explanation":"How many certifications do they have? Investing in your technology?","type":"quantitative","format":"number_range","unit":"certs","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"0"},"2":{"min":"1","max":"2"},"3":{"min":"3","max":"5"},"4":{"min":"6","max":"10"},"5":{"min":"11","max":""}}},
    {"id":19,"key":"sales_support_calls","name":"Sales support calls received","explanation":"Calling because of big pipeline, or because they can't sell your solution?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive calls from lack of product knowledge","2":"Frequent calls on routine questions","3":"Moderate — mix of pipeline-driven & knowledge gaps","4":"Mostly deal-strategy-driven; few basic questions","5":"Rare calls, always tied to complex high-value deals"}},
    {"id":20,"key":"tech_support_calls","name":"Tech support calls received","explanation":"Are they calling a lot because they lack proper training and certifications?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive calls; clear training gaps","2":"Frequent calls on issues certs should cover","3":"Average volume; occasional routine escalations","4":"Low volume; mostly complex edge-case questions","5":"Minimal calls; self-sufficient, resolves in-house"}},
    {"id":21,"key":"dedication_vs_competitive","name":"Dedication vs. competitive products","explanation":"Are you the strategic vendor, or do they prefer a competitor?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Sells competitor as primary; you're an afterthought","2":"Competitor is default; sells you only when asked","3":"Sells both roughly equally; no clear preference","4":"You are the preferred vendor; competitor secondary","5":"Exclusively or overwhelmingly sells your solution"}},
    {"id":22,"key":"dedication_vs_other_vendors","name":"Dedication vs. other vendors","explanation":"What % of their overall business does your solution represent?","type":"quantitative","format":"percentage_range","unit":"%","direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"5","max":"15"},"3":{"min":"15","max":"30"},"4":{"min":"30","max":"50"},"5":{"min":"50","max":"100"}}},
    {"id":23,"key":"geographical_coverage","name":"Geographical market coverage","explanation":"Right-sized territory? Covering too much? Potential to expand?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Very limited local presence; no expansion capacity","2":"Small territory; gaps in coverage","3":"Adequate regional coverage; some white space","4":"Strong multi-region, aligned with vendor targets","5":"National/intl coverage or dominant in key markets"}},
    {"id":24,"key":"vertical_coverage","name":"Vertical market coverage","explanation":"Specialize in certain verticals? Large existing customer base?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"No vertical focus; generalist with thin expertise","2":"Emerging in 1 vertical; small customer base","3":"Established in 1-2 verticals; moderate base","4":"Strong domain expertise; recognized in verticals","5":"Dominant authority; deep base & thought leadership"}},
    {"id":25,"key":"quality_of_management","name":"Quality of management","explanation":"Subjective — how well do they run their overall business?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Poor — disorganized, high turnover, unclear strategy","2":"Below average — reactive, inconsistent execution","3":"Adequate — competent but no stand-out leadership","4":"Strong — proactive, clear strategy, stable team","5":"Exceptional — visionary leadership, strong culture"}},
    {"id":26,"key":"known_litigation","name":"Known litigation (No=5, Yes=1)","explanation":"Are they involved in any lawsuits?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Active major litigation; existential/reputational risk","2":"Active litigation with material financial exposure","3":"Minor pending litigation; low-severity disputes","4":"Past litigation fully resolved; no current cases","5":"No known litigation history"}},
    {"id":27,"key":"export_control_ip","name":"Export control & IP protection","explanation":"Are they complying with export control and IP provisions?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Known violations or serious non-compliance","2":"Gaps identified; remediation not started","3":"Generally compliant; minor issues in audit","4":"Fully compliant; proactive internal controls","5":"Best-in-class compliance; clean audit history"}},
    {"id":28,"key":"financial_strength","name":"Financial strength","explanation":"Struggling with cash flow, or strong margins and financial resources?","type":"qualitative","format":"descriptor_scale","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Severe cash-flow issues; risk of insolvency","2":"Thin margins; late payments or credit concerns","3":"Stable but modest financial position","4":"Healthy margins and reserves; consistent profitability","5":"Very strong financials; well-capitalized, growing"}},
]

CATEGORIES = [
    {"label":"Revenue & Growth","icon":"💰","keys":["annual_revenues","yoy_revenue_growth","net_new_logo_revenues","pct_revenues_saas","net_revenue_expansion","total_revenues"]},
    {"label":"Sales Performance","icon":"📈","keys":["average_deal_size","avg_time_to_close","registered_deals","win_loss_ratio","partner_generated_opps_pct","frequency_of_business"]},
    {"label":"Retention & Satisfaction","icon":"🤝","keys":["renewal_rate","customer_satisfaction","communication_with_vendor"]},
    {"label":"Enablement & Support","icon":"🎓","keys":["mdf_utilization_rate","quality_of_sales_org","vendor_certifications","sales_support_calls","tech_support_calls"]},
    {"label":"Strategic Fit","icon":"🧭","keys":["dedication_vs_competitive","dedication_vs_other_vendors","geographical_coverage","vertical_coverage"]},
    {"label":"Risk & Governance","icon":"🛡️","keys":["quality_of_management","known_litigation","export_control_ip","financial_strength"]},
]

METRICS_BY_KEY = {m["key"]: m for m in SCORECARD_METRICS}
SAVE_PATH = pathlib.Path("scoring_criteria.json")
RESULTS_PATH = pathlib.Path("partner_results.json")
MAX_SCORE = len(SCORECARD_METRICS) * 5  # 140


# ═════════════════════════════════════════════════════════════════════════
# 1.  HELPERS
# ═════════════════════════════════════════════════════════════════════════

def _safe_float(val: str) -> float | None:
    """Parse a string to float, stripping $, commas, %, whitespace."""
    if val is None:
        return None
    cleaned = re.sub(r"[,$%\s]", "", str(val).strip())
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _init_criteria_state() -> None:
    """Seed criteria from disk or defaults into session state."""
    if "criteria" in st.session_state:
        return
    if SAVE_PATH.exists():
        try:
            st.session_state["criteria"] = json.loads(SAVE_PATH.read_text())
            return
        except Exception:
            pass
    # Build from defaults
    crit = {}
    for m in SCORECARD_METRICS:
        k = m["key"]
        if m["type"] == "quantitative":
            crit[k] = {"name":m["name"],"type":"quantitative","format":m["format"],
                        "unit":m["unit"],"direction":m["direction"],
                        "ranges":{s:{"min":m["defaults"][s]["min"],"max":m["defaults"][s]["max"]} for s in ("1","2","3","4","5")}}
        else:
            crit[k] = {"name":m["name"],"type":"qualitative","format":"descriptor_scale",
                        "unit":None,"direction":m["direction"],
                        "descriptors":{s:m["defaults"][s] for s in ("1","2","3","4","5")}}
    st.session_state["criteria"] = crit


def _save_criteria_from_form() -> None:
    """Collect Phase-1 form widgets → criteria dict → disk."""
    crit = st.session_state["criteria"]
    for m in SCORECARD_METRICS:
        mk = m["key"]
        if m["type"] == "quantitative":
            for s in ("1","2","3","4","5"):
                crit[mk]["ranges"][s]["min"] = st.session_state.get(f"p1_{mk}_s{s}_min", "")
                crit[mk]["ranges"][s]["max"] = st.session_state.get(f"p1_{mk}_s{s}_max", "")
        else:
            for s in ("1","2","3","4","5"):
                crit[mk]["descriptors"][s] = st.session_state.get(f"p1_{mk}_s{s}_desc", "")
    SAVE_PATH.write_text(json.dumps(crit, indent=2))


def compute_score(metric_key: str, performance_value) -> int | None:
    """
    Given a metric key and a raw performance value, return the 1-5 score
    by matching against the saved criteria ranges.

    Quantitative: parse performance as a number, check which range it falls in.
    Qualitative:  performance is the score-level string selected by the user;
                  return the level number directly.
    Returns None if scoring cannot be determined.
    """
    crit = st.session_state["criteria"].get(metric_key)
    if not crit:
        return None

    if crit["type"] == "quantitative":
        val = _safe_float(performance_value)
        if val is None:
            return None
        # Walk scores 5→1 (check best first) for higher_is_better,
        # or 5→1 for lower_is_better (ranges are already inverted in data)
        for s in ("5", "4", "3", "2", "1"):
            r = crit["ranges"][s]
            lo = _safe_float(r["min"])
            hi = _safe_float(r["max"])
            if lo is not None and hi is not None:
                if lo <= val <= hi:
                    return int(s)
            elif lo is not None and hi is None:
                if val >= lo:
                    return int(s)
            elif lo is None and hi is not None:
                if val <= hi:
                    return int(s)
        return 1  # fallback
    else:
        # Qualitative — performance_value is the chosen level string
        if not performance_value or performance_value == "— Select —":
            return None
        for s in ("1","2","3","4","5"):
            if crit["descriptors"][s] == performance_value:
                return int(s)
        return None


def _score_color(score: int | None) -> str:
    if score is None:
        return "#999"
    return {1:"#dc4040",2:"#e8820c",3:"#d4a917",4:"#49a34f",5:"#1b6e23"}.get(score,"#999")


def _grade_label(pct: float) -> tuple[str, str]:
    """Return (letter grade, color)."""
    if pct >= 90: return "A", "#1b6e23"
    if pct >= 80: return "B+", "#49a34f"
    if pct >= 70: return "B", "#6aab2e"
    if pct >= 60: return "C+", "#d4a917"
    if pct >= 50: return "C", "#e8820c"
    return "D", "#dc4040"


# ═════════════════════════════════════════════════════════════════════════
# 2.  PAGE CONFIG & CSS
# ═════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Partner Scorecard", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"] { background: #f3f5f9; font-family: 'DM Sans', sans-serif; }
section[data-testid="stSidebar"] { background: linear-gradient(195deg,#162033,#1e2d45); }
section[data-testid="stSidebar"] * { color: #c4cfde !important; }
section[data-testid="stSidebar"] hr { border-color: #2a3d57 !important; }

.phase-header { font-size:1.65rem; font-weight:800; color:#1e2a3a; margin:0 0 4px; }
.phase-sub { font-size:.92rem; color:#5a6a7e; margin:0 0 18px; line-height:1.55; }

.mc { background:#fff; border:1px solid #e2e6ed; border-radius:14px;
      padding:20px 24px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,.03); }
.mc:hover { border-color:#b0bdd0; box-shadow:0 4px 16px rgba(0,0,0,.07); }

.mname { font-size:1.02rem; font-weight:700; color:#1e2a3a; }
.mexpl { font-size:.83rem; color:#5a6a7e; margin:2px 0 10px; line-height:1.45; }

.tag { font-size:.68rem; font-weight:700; padding:2px 9px; border-radius:20px;
       text-transform:uppercase; letter-spacing:.04em; display:inline-block; margin-left:6px; }
.tag-q { background:#dbe8ff; color:#1c5dbf; }
.tag-ql { background:#eedeff; color:#6b3fa0; }
.tag-hi { background:#e3f5e5; color:#2e7d32; }
.tag-lo { background:#fff3e0; color:#e65100; }

.sb { display:inline-flex; align-items:center; justify-content:center;
      width:28px; height:28px; border-radius:8px; font-size:.78rem;
      font-weight:800; color:#fff; margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.sb1{background:#dc4040}.sb2{background:#e8820c}.sb3{background:#d4a917;color:#333!important}
.sb4{background:#49a34f}.sb5{background:#1b6e23}

.toast { background:#1b6e23; color:#fff; padding:.7rem 1.2rem; border-radius:10px;
         font-weight:600; text-align:center; margin-bottom:1rem; }

/* Results table */
.res-tbl { width:100%; border-collapse:separate; border-spacing:0;
           border:1px solid #e2e6ed; border-radius:12px; overflow:hidden;
           font-size:.88rem; background:#fff; margin:1rem 0; }
.res-tbl th { background:#1e2a3a; color:#fff; padding:10px 14px; text-align:left;
              font-weight:700; font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }
.res-tbl td { padding:10px 14px; border-top:1px solid #eef0f5; }
.res-tbl tr:hover td { background:#f6f8fc; }

.score-pill { display:inline-block; padding:3px 14px; border-radius:20px;
              font-weight:800; font-size:.82rem; color:#fff; min-width:28px; text-align:center;
              font-family:'JetBrains Mono',monospace; }

/* Summary cards */
.sum-card { background:linear-gradient(135deg,#1e2a3a,#2c3e56); border-radius:14px;
            padding:22px 24px; color:#fff; text-align:center; }
.sum-big { font-size:2.4rem; font-weight:800; font-family:'JetBrains Mono',monospace; }
.sum-lbl { font-size:.75rem; opacity:.7; text-transform:uppercase; letter-spacing:.06em; margin-top:2px; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# 3.  INIT STATE
# ═════════════════════════════════════════════════════════════════════════

_init_criteria_state()

# ═════════════════════════════════════════════════════════════════════════
# 4.  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 📋 Partner Scorecard")
    st.markdown("---")
    phase = st.radio(
        "Select Phase",
        ["Phase 1 — Define Criteria", "Phase 2 — Score Partner"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Category filter (used in both phases)
    cat_labels = ["All Metrics"] + [f"{c['icon']}  {c['label']}" for c in CATEGORIES]
    chosen_cat = st.radio("Category filter", cat_labels, index=0, label_visibility="collapsed")

    st.markdown("---")
    criteria_ready = SAVE_PATH.exists()
    if criteria_ready:
        st.success("✅ Criteria saved")
    else:
        st.info("ℹ️ Save Phase 1 criteria first")

    quant_n = sum(1 for m in SCORECARD_METRICS if m["type"]=="quantitative")
    col_a, col_b = st.columns(2)
    col_a.metric("Quantitative", quant_n)
    col_b.metric("Qualitative", len(SCORECARD_METRICS)-quant_n)


# ── Filter visible metrics ────────────────────────────────────────────
if chosen_cat == "All Metrics":
    visible_metrics = SCORECARD_METRICS
else:
    cat_name = chosen_cat.split("  ",1)[-1]
    cat_keys = next(c["keys"] for c in CATEGORIES if c["label"]==cat_name)
    visible_metrics = [METRICS_BY_KEY[k] for k in cat_keys]


# ═════════════════════════════════════════════════════════════════════════
# 5.  PHASE 1 — DEFINE CRITERIA
# ═════════════════════════════════════════════════════════════════════════

if phase == "Phase 1 — Define Criteria":
    st.markdown('<div class="phase-header">Phase 1 — Define Scoring Criteria</div>', unsafe_allow_html=True)
    st.markdown('<div class="phase-sub">Configure the <b>1–5 scoring thresholds</b> for each metric. Quantitative → numeric min/max; Qualitative → text descriptors. Defaults are pre-filled.</div>', unsafe_allow_html=True)

    if st.session_state.get("_p1_saved"):
        st.markdown('<div class="toast">✅ Criteria saved to scoring_criteria.json</div>', unsafe_allow_html=True)
        st.session_state["_p1_saved"] = False

    with st.form("phase1_form"):
        for m in visible_metrics:
            mk = m["key"]
            crit = st.session_state["criteria"][mk]
            is_q = m["type"]=="quantitative"

            type_tag = '<span class="tag tag-q">Quantitative</span>' if is_q else '<span class="tag tag-ql">Qualitative</span>'
            dir_tag = f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
            unit_d = f' ({m["unit"]})' if m.get("unit") else ""

            st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{type_tag}{dir_tag}<div class="mexpl">{m["explanation"]}</div></div>', unsafe_allow_html=True)

            if is_q:
                cols = st.columns(5)
                for idx, s in enumerate(("1","2","3","4","5")):
                    with cols[idx]:
                        st.markdown(f'<div class="sb sb{s}">{s}</div>', unsafe_allow_html=True)
                        st.text_input(f"Min{unit_d}", value=crit["ranges"][s]["min"],
                                      key=f"p1_{mk}_s{s}_min", placeholder="No min" if s=="1" else "")
                        st.text_input(f"Max{unit_d}", value=crit["ranges"][s]["max"],
                                      key=f"p1_{mk}_s{s}_max", placeholder="No cap" if s=="5" else "")
            else:
                cols = st.columns(5)
                for idx, s in enumerate(("1","2","3","4","5")):
                    with cols[idx]:
                        st.markdown(f'<div class="sb sb{s}">{s}</div>', unsafe_allow_html=True)
                        st.text_area("desc", value=crit["descriptors"][s],
                                     key=f"p1_{mk}_s{s}_desc", height=100, label_visibility="collapsed")

        st.markdown("---")
        _, _, rc = st.columns([2,2,1])
        with rc:
            submitted = st.form_submit_button("💾  Save Criteria", use_container_width=True, type="primary")

    if submitted:
        _save_criteria_from_form()
        st.session_state["_p1_saved"] = True
        st.rerun()

    if SAVE_PATH.exists():
        st.markdown("---")
        with st.expander("📄 Preview / Download scoring_criteria.json"):
            raw = SAVE_PATH.read_text()
            st.code(raw, language="json")
            st.download_button("⬇️ Download JSON", raw, "scoring_criteria.json", "application/json")


# ═════════════════════════════════════════════════════════════════════════
# 6.  PHASE 2 — SCORE A PARTNER
# ═════════════════════════════════════════════════════════════════════════

else:
    st.markdown('<div class="phase-header">Phase 2 — Score a Partner</div>', unsafe_allow_html=True)

    if not SAVE_PATH.exists():
        st.warning("⚠️ No scoring criteria found. Please complete **Phase 1** first and save criteria.")
        st.stop()

    # Reload criteria from disk so we have latest
    st.session_state["criteria"] = json.loads(SAVE_PATH.read_text())
    crit = st.session_state["criteria"]

    st.markdown('<div class="phase-sub">Enter partner performance data below. Scores are <b>auto-calculated</b> on submit by matching values to your Phase 1 criteria. Total is out of <b>140</b> (28 × 5).</div>', unsafe_allow_html=True)

    # Show results if they exist
    if st.session_state.get("_p2_results"):
        res = st.session_state["_p2_results"]
        partner = res["partner_name"]
        rows = res["rows"]
        total = res["total_score"]
        scored_n = res["scored_count"]
        max_possible = scored_n * 5
        pct = (total / max_possible * 100) if max_possible else 0
        grade, grade_color = _grade_label(pct)

        st.markdown(f"### Results for **{partner}**")

        # Summary cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="sum-card"><div class="sum-big">{total}</div><div class="sum-lbl">Total Score</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="sum-card"><div class="sum-big">{total}/{max_possible}</div><div class="sum-lbl">Scored / Max</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="sum-card"><div class="sum-big">{pct:.1f}%</div><div class="sum-lbl">Percentage</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:{grade_color}">{grade}</div><div class="sum-lbl">Grade</div></div>', unsafe_allow_html=True)

        # Results table
        tbl_rows = ""
        for r in rows:
            sc = r["score"]
            sc_color = _score_color(sc)
            sc_display = f'<span class="score-pill" style="background:{sc_color}">{sc}</span>' if sc else '<span style="color:#999">—</span>'
            perf_display = r["performance"] if r["performance"] else '<span style="color:#999">—</span>'
            type_tag = '<span class="tag tag-q">Q</span>' if r["type"]=="quantitative" else '<span class="tag tag-ql">QL</span>'
            tbl_rows += f'<tr><td>{r["id"]}</td><td>{r["name"]} {type_tag}</td><td>{perf_display}</td><td>{sc_display}</td></tr>'

        st.markdown(f"""
        <table class="res-tbl">
        <thead><tr><th>#</th><th>Metric</th><th>Performance</th><th>Score</th></tr></thead>
        <tbody>{tbl_rows}
        <tr style="background:#f0f2f7; font-weight:700;">
            <td colspan="3" style="text-align:right; font-size:.92rem;">TOTAL</td>
            <td><span class="score-pill" style="background:#1e2a3a">{total} / {max_possible}</span> &nbsp; ({pct:.1f}%)</td>
        </tr>
        </tbody></table>
        """, unsafe_allow_html=True)

        # Download results
        results_json = json.dumps(res, indent=2)
        col_dl1, col_dl2, _ = st.columns([1,1,2])
        with col_dl1:
            st.download_button("⬇️ Download Results JSON", results_json, f"{partner.replace(' ','_')}_scorecard.json", "application/json")

        st.markdown("---")

    # ── PARTNER INPUT FORM ────────────────────────────────────────────
    st.markdown("### Enter Partner Performance")

    with st.form("phase2_form"):
        partner_name = st.text_input(
            "🏢 Partner Name",
            value=st.session_state.get("_p2_partner_name", ""),
            placeholder="e.g. Acme Solutions Inc.",
        )

        st.markdown("---")

        for m in visible_metrics:
            mk = m["key"]
            mc = crit[mk]
            is_q = m["type"]=="quantitative"
            type_tag = '<span class="tag tag-q">Quantitative</span>' if is_q else '<span class="tag tag-ql">Qualitative</span>'
            dir_tag = f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'

            st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{type_tag}{dir_tag}<div class="mexpl">{m["explanation"]}</div></div>', unsafe_allow_html=True)

            if is_q:
                # Show the ranges as a hint
                unit = mc.get("unit","") or ""
                hints = []
                for s in ("1","2","3","4","5"):
                    r = mc["ranges"][s]
                    lo, hi = r["min"], r["max"]
                    if lo and hi:
                        hints.append(f"**{s}**: {lo}–{hi}")
                    elif lo and not hi:
                        hints.append(f"**{s}**: ≥{lo}")
                    elif not lo and hi:
                        hints.append(f"**{s}**: ≤{hi}")
                hint_str = f"Ranges ({unit}): " + " · ".join(hints) if hints else ""
                st.caption(hint_str)

                st.text_input(
                    f"Performance value ({unit})",
                    key=f"p2_{mk}_perf",
                    placeholder=f"Enter a number ({unit})",
                )
            else:
                # Qualitative — dropdown of descriptors
                options = ["— Select —"] + [mc["descriptors"][s] for s in ("1","2","3","4","5")]
                st.selectbox(
                    "Select performance level",
                    options,
                    key=f"p2_{mk}_perf",
                )

        st.markdown("---")
        _, _, rc = st.columns([2,2,1])
        with rc:
            p2_submitted = st.form_submit_button("🧮  Calculate Scores", use_container_width=True, type="primary")

    if p2_submitted:
        if not partner_name.strip():
            st.error("Please enter a partner name.")
            st.stop()

        st.session_state["_p2_partner_name"] = partner_name.strip()

        rows = []
        total = 0
        scored = 0
        for m in SCORECARD_METRICS:
            mk = m["key"]
            perf_val = st.session_state.get(f"p2_{mk}_perf", "")
            score = compute_score(mk, perf_val)

            display_perf = perf_val if perf_val and perf_val != "— Select —" else ""
            # For quantitative, trim for display
            if m["type"]=="quantitative" and display_perf:
                num = _safe_float(display_perf)
                if num is not None:
                    unit = m.get("unit","") or ""
                    if unit == "$":
                        display_perf = f"${num:,.0f}"
                    elif unit == "%":
                        display_perf = f"{num:g}%"
                    else:
                        display_perf = f"{num:g} {unit}".strip()

            rows.append({
                "id": m["id"],
                "key": mk,
                "name": m["name"],
                "type": m["type"],
                "performance": display_perf,
                "score": score,
            })
            if score is not None:
                total += score
                scored += 1

        st.session_state["_p2_results"] = {
            "partner_name": partner_name.strip(),
            "rows": rows,
            "total_score": total,
            "scored_count": scored,
            "max_possible": scored * 5,
            "percentage": round(total / (scored*5) * 100, 1) if scored else 0,
        }
        st.rerun()

