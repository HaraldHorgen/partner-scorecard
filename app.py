"""
ChannelPRO — Partner Revenue Optimizer
=======================================
Client Intake  → Phase 1 (Scoring Criteria) → Phase 2 (Score Partner)

Run:  streamlit run app.py
"""

import json, pathlib, re
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
CLIENT_PATH = pathlib.Path("client_info.json")
MAX_SCORE = len(SCORECARD_METRICS) * 5  # 140


# ═════════════════════════════════════════════════════════════════════════
# 1.  HELPERS
# ═════════════════════════════════════════════════════════════════════════

def _safe_float(val) -> float | None:
    if val is None: return None
    cleaned = re.sub(r"[,$%\s]", "", str(val).strip())
    if cleaned == "": return None
    try: return float(cleaned)
    except ValueError: return None

def _init_criteria_state():
    if "criteria" in st.session_state: return
    if SAVE_PATH.exists():
        try:
            st.session_state["criteria"] = json.loads(SAVE_PATH.read_text())
            return
        except Exception: pass
    crit = {}
    for m in SCORECARD_METRICS:
        k = m["key"]
        if m["type"] == "quantitative":
            crit[k] = {"name":m["name"],"type":"quantitative","format":m["format"],"unit":m["unit"],"direction":m["direction"],"ranges":{s:{"min":m["defaults"][s]["min"],"max":m["defaults"][s]["max"]} for s in ("1","2","3","4","5")}}
        else:
            crit[k] = {"name":m["name"],"type":"qualitative","format":"descriptor_scale","unit":None,"direction":m["direction"],"descriptors":{s:m["defaults"][s] for s in ("1","2","3","4","5")}}
    st.session_state["criteria"] = crit

def _save_criteria_from_form():
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

def compute_score(metric_key, performance_value):
    crit = st.session_state["criteria"].get(metric_key)
    if not crit: return None
    if crit["type"] == "quantitative":
        val = _safe_float(performance_value)
        if val is None: return None
        for s in ("5","4","3","2","1"):
            r = crit["ranges"][s]
            lo, hi = _safe_float(r["min"]), _safe_float(r["max"])
            if lo is not None and hi is not None and lo <= val <= hi: return int(s)
            if lo is not None and hi is None and val >= lo: return int(s)
            if lo is None and hi is not None and val <= hi: return int(s)
        return 1
    else:
        if not performance_value or performance_value == "— Select —": return None
        for s in ("1","2","3","4","5"):
            if crit["descriptors"][s] == performance_value: return int(s)
        return None

def _score_color(score):
    if score is None: return "#999"
    return {1:"#dc4040",2:"#e8820c",3:"#d4a917",4:"#49a34f",5:"#1b6e23"}.get(score,"#999")

def _grade_label(pct):
    if pct >= 90: return "A","#1b6e23"
    if pct >= 80: return "B+","#49a34f"
    if pct >= 70: return "B","#6aab2e"
    if pct >= 60: return "C+","#d4a917"
    if pct >= 50: return "C","#e8820c"
    return "D","#dc4040"

def _navigate_to(page):
    st.session_state["current_page"] = page

# ═════════════════════════════════════════════════════════════════════════
# 2.  PAGE CONFIG & CSS
# ═════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="ChannelPRO — Partner Revenue Optimizer", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"] { background: #f3f5f9; font-family: 'DM Sans', sans-serif; }
section[data-testid="stSidebar"] { background: linear-gradient(195deg,#162033,#1e2d45); }
section[data-testid="stSidebar"] * { color: #c4cfde !important; }
section[data-testid="stSidebar"] hr { border-color: #2a3d57 !important; }

/* Brand header */
.brand-bar { display:flex; align-items:center; gap:14px; margin-bottom:4px; }
.brand-logo { width:48px; height:48px; border-radius:10px;
    background:linear-gradient(135deg,#2563eb,#1b4fd4); display:flex;
    align-items:center; justify-content:center; font-size:22px; color:#fff; font-weight:800; }
.brand-title { font-size:2rem; font-weight:800; color:#1e2a3a;
    font-family:'DM Sans',sans-serif; letter-spacing:-0.02em; }
.brand-sub { font-size:1.1rem; color:#4a6a8f; font-weight:600; margin-top:-4px; }

/* Info box */
.info-box { background:#f0f2f7; border-left:4px solid #2563eb; border-radius:8px;
    padding:22px 26px; margin:20px 0 28px; line-height:1.7; color:#2c3e56; font-size:.92rem; }
.info-box ol { margin:10px 0 10px 18px; padding:0; }
.info-box ol li { margin-bottom:4px; }

/* Cards */
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
.sum-card { background:linear-gradient(135deg,#1e2a3a,#2c3e56); border-radius:14px;
            padding:22px 24px; color:#fff; text-align:center; }
.sum-big { font-size:2.4rem; font-weight:800; font-family:'JetBrains Mono',monospace; }
.sum-lbl { font-size:.75rem; opacity:.7; text-transform:uppercase; letter-spacing:.06em; margin-top:2px; }

/* Section headers on intake */
.sec-head { font-size:1.15rem; font-weight:800; color:#1e2a3a; margin:28px 0 12px;
            padding-bottom:8px; border-bottom:2px solid #e2e6ed; }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════
# 3.  INIT STATE
# ═════════════════════════════════════════════════════════════════════════

_init_criteria_state()
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Client Intake"

# Load saved client info
if "client_info" not in st.session_state:
    if CLIENT_PATH.exists():
        try: st.session_state["client_info"] = json.loads(CLIENT_PATH.read_text())
        except Exception: st.session_state["client_info"] = {}
    else:
        st.session_state["client_info"] = {}


# ═════════════════════════════════════════════════════════════════════════
# 4.  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Branding in sidebar
    st.markdown("## 📋 ChannelPRO")
    st.markdown("**Partner Revenue Optimizer**")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["Client Intake", "Phase 1 — Scoring Criteria", "Phase 2 — Score Partner"],
        index=["Client Intake","Phase 1 — Scoring Criteria","Phase 2 — Score Partner"].index(st.session_state["current_page"]),
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state["current_page"] = page

    st.markdown("---")

    # Category filter (for Phase 1 & 2)
    if page != "Client Intake":
        cat_labels = ["All Metrics"] + [f"{c['icon']}  {c['label']}" for c in CATEGORIES]
        chosen_cat = st.radio("Category filter", cat_labels, index=0, label_visibility="collapsed")
    else:
        chosen_cat = "All Metrics"

    st.markdown("---")
    criteria_ready = SAVE_PATH.exists()
    if criteria_ready:
        st.success("✅ Criteria saved")
    else:
        st.info("ℹ️ Complete Phase 1 first")

    quant_n = sum(1 for m in SCORECARD_METRICS if m["type"]=="quantitative")
    col_a, col_b = st.columns(2)
    col_a.metric("Quantitative", quant_n)
    col_b.metric("Qualitative", len(SCORECARD_METRICS)-quant_n)


# Filter visible metrics
if chosen_cat == "All Metrics":
    visible_metrics = SCORECARD_METRICS
else:
    cat_name = chosen_cat.split("  ",1)[-1]
    cat_keys = next(c["keys"] for c in CATEGORIES if c["label"]==cat_name)
    visible_metrics = [METRICS_BY_KEY[k] for k in cat_keys]


# ═════════════════════════════════════════════════════════════════════════
# 5.  CLIENT INTAKE PAGE
# ═════════════════════════════════════════════════════════════════════════

if page == "Client Intake":

    # ── Brand header ──────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-bottom:8px;">
        <div class="brand-bar" style="justify-content:center;">
            <div class="brand-logo">C</div>
            <div>
                <div class="brand-title">ChannelPRO</div>
            </div>
        </div>
        <div class="brand-sub">Partner Revenue Optimizer</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Description box ───────────────────────────────────────────────
    st.markdown("""
    <div class="info-box">
        The <b>Partner Revenue Optimizer</b> is a structured process that will:
        <ol>
            <li>Right-size the margins you provide to your partners, freeing up significant cash flow and revenues for you; and</li>
            <li>Lay the foundation for targeted partner marketing programs to drive more revenues from new and existing partners.</li>
        </ol>
        <p>An experienced channel consultant from <b>The York Group</b> will guide you through the process of establishing the right metrics to measure your partners' relative performance. Some of them, such as revenue-related metrics, will be readily available from your accounting, CRM and PRM systems, while others will be more subjective. It is likely that some of the metrics we ask for are not currently being tracked, and that is OK. We will explain how they would add value to your current program, and you can decide whether they should be tracked in the future.</p>
        <p>Each metric will be rated on a scale of <b>1–5</b>, with 5 being the best in each case. These scores will be used in the next step, which is to review and score each of your partners. The individual partner scores will be fed into a heat map that shows the performance of all of your partners across all of the metrics you have selected.</p>
        <p>The scores you establish are foundational for the next steps in the process, so please take the time you need to understand each metric and the scores that should be assigned.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("_client_saved"):
        st.markdown('<div class="toast">✅ Client information saved</div>', unsafe_allow_html=True)
        st.session_state["_client_saved"] = False

    ci = st.session_state["client_info"]

    with st.form("client_intake_form"):

        # ── Section 1: Client Contact Information ─────────────────────
        st.markdown('<div class="sec-head">📇 Client Contact Information</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client name", value=ci.get("client_name",""), key="ci_name")
            client_url = st.text_input("URL", value=ci.get("url",""), placeholder="https://...", key="ci_url")
            client_country = st.text_input("Country", value=ci.get("country",""), key="ci_country")
            client_phone = st.text_input("Primary phone", value=ci.get("phone",""), key="ci_phone")
        with col2:
            client_pm = st.text_input("Client project manager", value=ci.get("project_manager",""), key="ci_pm")
            client_city = st.text_input("City", value=ci.get("city",""), key="ci_city")
            client_email = st.text_input("Primary contact email", value=ci.get("email",""), key="ci_email")

        # ── Section 2: Client Business Information ────────────────────
        st.markdown('<div class="sec-head">🏢 Client Business Information</div>', unsafe_allow_html=True)

        # Company size
        st.markdown("**What size company do you typically sell to? What segment represents the majority of your sales?** *(Select no more than two)*")
        size_options = ["<100", "100-200", "200-500", "500-1,000", "1,000-5,000", ">5,000"]
        saved_sizes = ci.get("company_size", [])
        size_cols = st.columns(len(size_options))
        sizes_selected = []
        for i, opt in enumerate(size_options):
            with size_cols[i]:
                if st.checkbox(opt, value=opt in saved_sizes, key=f"ci_size_{i}"):
                    sizes_selected.append(opt)

        st.markdown("")  # spacer

        # Verticals
        st.markdown("**Are there specific verticals you sell to?**")
        vertical_options = [
            "Manufacturing", "Automotive", "Health care",
            "Financial services", "Retail", "Government",
            "Education", "Media and entertainment",
            "Professional services", "Life sciences, pharmaceuticals",
            "High-tech, electronics, communications, telecom",
            "None - we have a horizontal solution",
        ]
        saved_verts = ci.get("verticals", [])
        vert_cols_a = st.columns(3)
        verts_selected = []
        for i, opt in enumerate(vertical_options):
            with vert_cols_a[i % 3]:
                if st.checkbox(opt, value=opt in saved_verts, key=f"ci_vert_{i}"):
                    verts_selected.append(opt)
        other_verts = st.text_input("Other verticals", value=ci.get("other_verticals",""), key="ci_other_verts")

        st.markdown("")

        # Solution delivery
        st.markdown("**How is the solution delivered?** *(Check all that apply)*")
        delivery_options = ["On-premise", "SaaS/PaaS", "IaaS/VM", "As a device (hardware and software)"]
        saved_delivery = ci.get("solution_delivery", [])
        del_cols = st.columns(len(delivery_options))
        delivery_selected = []
        for i, opt in enumerate(delivery_options):
            with del_cols[i]:
                if st.checkbox(opt, value=opt in saved_delivery, key=f"ci_del_{i}"):
                    delivery_selected.append(opt)

        st.markdown("")

        # Average first-year transaction value
        st.markdown("**Average first-year transaction value of the solution itself**, not including deployment services, software assurance, maintenance or customization.")
        txn_options = ["Under $1,000", "$1,000-$10,000", "$10,000-$50,000", "$50,000-$100,000", "More than $100,000"]
        saved_txn = ci.get("avg_transaction_value", "")
        txn_value = st.radio("Select range", txn_options, index=txn_options.index(saved_txn) if saved_txn in txn_options else 0, key="ci_txn", horizontal=True)

        st.markdown("")

        # Services percentage
        st.markdown("**Services as part of the transaction** (not including maintenance). As a percentage of the software license or first-year subscription, how much does a client spend on services such as installation, integration, customization, training, etc.?")
        svc_options = ["No services", "<20%", "20-50%", "50-200%", ">200%"]
        saved_svc = ci.get("services_pct", "")
        svc_value = st.radio("Select range", svc_options, index=svc_options.index(saved_svc) if saved_svc in svc_options else 0, key="ci_svc", horizontal=True)
        svc_comments = st.text_input("Comments (services)", value=ci.get("services_comments",""), key="ci_svc_comments")

        st.markdown("")

        # Number of partners
        st.markdown("**How many resellers/channel partners do you have?**")
        partner_count_opts = ["<100", "100-200", "200-500", "500-1,000", "1,000-5,000", ">5,000"]
        saved_pc = ci.get("partner_count", "")
        partner_count = st.radio("Select range", partner_count_opts, index=partner_count_opts.index(saved_pc) if saved_pc in partner_count_opts else 0, key="ci_pc", horizontal=True)

        st.markdown("")

        # Revenue from indirect channels
        st.markdown("**Percentage of revenues that come from indirect channels.**")
        indirect_opts = ["<10%", "10-30%", "30-50%", ">50%"]
        saved_indirect = ci.get("indirect_revenue_pct", "")
        indirect_pct = st.radio("Select range", indirect_opts, index=indirect_opts.index(saved_indirect) if saved_indirect in indirect_opts else 0, key="ci_indirect", horizontal=True)

        st.markdown("")

        # Discounts
        st.markdown("**What are the discounts currently given to channel partners?** *(Select all that apply)*")
        disc_options = ["<15%", "15-30%", "30-50%", ">60%", "Other"]
        saved_disc = ci.get("discounts", [])
        disc_cols = st.columns(len(disc_options))
        disc_selected = []
        for i, opt in enumerate(disc_options):
            with disc_cols[i]:
                if st.checkbox(opt, value=opt in saved_disc, key=f"ci_disc_{i}"):
                    disc_selected.append(opt)

        st.markdown("")

        # Partner designations
        st.markdown("**Partner designations**")
        partner_desig = st.text_input(
            "Use comma-separated text, e.g. gold, silver, bronze",
            value=ci.get("partner_designations",""),
            key="ci_desig",
        )

        # ── Submit ────────────────────────────────────────────────────
        st.markdown("---")
        col_l, col_r = st.columns([3,1])
        with col_r:
            intake_submitted = st.form_submit_button("Next →  Phase 1", use_container_width=True, type="primary")

    if intake_submitted:
        # Save all client info
        st.session_state["client_info"] = {
            "client_name": client_name,
            "project_manager": client_pm,
            "url": client_url,
            "city": client_city,
            "country": client_country,
            "email": client_email,
            "phone": client_phone,
            "company_size": sizes_selected,
            "verticals": verts_selected,
            "other_verticals": other_verts,
            "solution_delivery": delivery_selected,
            "avg_transaction_value": txn_value,
            "services_pct": svc_value,
            "services_comments": svc_comments,
            "partner_count": partner_count,
            "indirect_revenue_pct": indirect_pct,
            "discounts": disc_selected,
            "partner_designations": partner_desig,
        }
        CLIENT_PATH.write_text(json.dumps(st.session_state["client_info"], indent=2))
        st.session_state["_client_saved"] = True
        st.session_state["current_page"] = "Phase 1 — Scoring Criteria"
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# 6.  PHASE 1 — DEFINE CRITERIA
# ═════════════════════════════════════════════════════════════════════════

elif page == "Phase 1 — Scoring Criteria":

    st.markdown("""
    <div class="brand-bar">
        <div class="brand-logo" style="width:36px;height:36px;font-size:16px;">C</div>
        <div><span style="font-size:1.1rem;font-weight:800;color:#1e2a3a;">ChannelPRO</span>
        <span style="font-size:.85rem;color:#5a6a7e;margin-left:8px;">Partner Revenue Optimizer</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Phase 1 — Define Scoring Criteria")
    st.markdown("Configure the **1–5 scoring thresholds** for each metric. Quantitative → numeric min/max; Qualitative → text descriptors. Defaults are pre-filled.")

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
                        st.text_input(f"Min{unit_d}", value=crit["ranges"][s]["min"], key=f"p1_{mk}_s{s}_min", placeholder="No min" if s=="1" else "")
                        st.text_input(f"Max{unit_d}", value=crit["ranges"][s]["max"], key=f"p1_{mk}_s{s}_max", placeholder="No cap" if s=="5" else "")
            else:
                cols = st.columns(5)
                for idx, s in enumerate(("1","2","3","4","5")):
                    with cols[idx]:
                        st.markdown(f'<div class="sb sb{s}">{s}</div>', unsafe_allow_html=True)
                        st.text_area("desc", value=crit["descriptors"][s], key=f"p1_{mk}_s{s}_desc", height=100, label_visibility="collapsed")

        st.markdown("---")
        col_l, col_m, col_r = st.columns([2,1,1])
        with col_m:
            p1_submitted = st.form_submit_button("💾  Save Criteria", use_container_width=True, type="primary")
        with col_r:
            p1_next = st.form_submit_button("Next →  Phase 2", use_container_width=True)

    if p1_submitted or p1_next:
        _save_criteria_from_form()
        st.session_state["_p1_saved"] = True
        if p1_next:
            st.session_state["current_page"] = "Phase 2 — Score Partner"
        st.rerun()

    if SAVE_PATH.exists():
        st.markdown("---")
        with st.expander("📄 Preview / Download scoring_criteria.json"):
            raw = SAVE_PATH.read_text()
            st.code(raw, language="json")
            st.download_button("⬇️ Download JSON", raw, "scoring_criteria.json", "application/json")


# ═════════════════════════════════════════════════════════════════════════
# 7.  PHASE 2 — SCORE A PARTNER
# ═════════════════════════════════════════════════════════════════════════

else:

    st.markdown("""
    <div class="brand-bar">
        <div class="brand-logo" style="width:36px;height:36px;font-size:16px;">C</div>
        <div><span style="font-size:1.1rem;font-weight:800;color:#1e2a3a;">ChannelPRO</span>
        <span style="font-size:.85rem;color:#5a6a7e;margin-left:8px;">Partner Revenue Optimizer</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Phase 2 — Score a Partner")

    if not SAVE_PATH.exists():
        st.warning("⚠️ No scoring criteria found. Please complete **Phase 1** first and save criteria.")
        st.stop()

    st.session_state["criteria"] = json.loads(SAVE_PATH.read_text())
    crit = st.session_state["criteria"]

    st.markdown("Enter partner performance data below. Scores are **auto-calculated** on submit by matching values to your Phase 1 criteria. Total is out of **140** (28 × 5).")

    # Show results
    if st.session_state.get("_p2_results"):
        res = st.session_state["_p2_results"]
        partner = res["partner_name"]
        rows = res["rows"]
        total = res["total_score"]
        scored_n = res["scored_count"]
        max_possible = scored_n * 5
        pct = (total / max_possible * 100) if max_possible else 0
        grade_l, grade_c = _grade_label(pct)

        st.markdown(f"### Results for **{partner}**")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="sum-card"><div class="sum-big">{total}</div><div class="sum-lbl">Total Score</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sum-card"><div class="sum-big">{total}/{max_possible}</div><div class="sum-lbl">Scored / Max</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="sum-card"><div class="sum-big">{pct:.1f}%</div><div class="sum-lbl">Percentage</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:{grade_c}">{grade_l}</div><div class="sum-lbl">Grade</div></div>', unsafe_allow_html=True)

        tbl_rows = ""
        for r in rows:
            sc = r["score"]
            sc_color = _score_color(sc)
            sc_display = f'<span class="score-pill" style="background:{sc_color}">{sc}</span>' if sc else '<span style="color:#999">—</span>'
            perf_display = r["performance"] if r["performance"] else '<span style="color:#999">—</span>'
            type_tag = '<span class="tag tag-q">Q</span>' if r["type"]=="quantitative" else '<span class="tag tag-ql">QL</span>'
            tbl_rows += f'<tr><td>{r["id"]}</td><td>{r["name"]} {type_tag}</td><td>{perf_display}</td><td>{sc_display}</td></tr>'
        st.markdown(f"""<table class="res-tbl">
        <thead><tr><th>#</th><th>Metric</th><th>Performance</th><th>Score</th></tr></thead>
        <tbody>{tbl_rows}
        <tr style="background:#f0f2f7;font-weight:700;"><td colspan="3" style="text-align:right;">TOTAL</td>
        <td><span class="score-pill" style="background:#1e2a3a">{total}/{max_possible}</span> ({pct:.1f}%)</td></tr></tbody></table>""", unsafe_allow_html=True)

        results_json = json.dumps(res, indent=2)
        st.download_button("⬇️ Download Results JSON", results_json, f"{partner.replace(' ','_')}_scorecard.json", "application/json")
        st.markdown("---")

    # Partner input form
    st.markdown("### Enter Partner Performance")
    with st.form("phase2_form"):
        partner_name = st.text_input("🏢 Partner Name", value=st.session_state.get("_p2_partner_name",""), placeholder="e.g. Acme Solutions Inc.")
        st.markdown("---")
        for m in visible_metrics:
            mk = m["key"]
            mc = crit[mk]
            is_q = m["type"]=="quantitative"
            type_tag = '<span class="tag tag-q">Quantitative</span>' if is_q else '<span class="tag tag-ql">Qualitative</span>'
            dir_tag = f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
            st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{type_tag}{dir_tag}<div class="mexpl">{m["explanation"]}</div></div>', unsafe_allow_html=True)
            if is_q:
                unit = mc.get("unit","") or ""
                hints = []
                for s in ("1","2","3","4","5"):
                    r = mc["ranges"][s]; lo,hi = r["min"],r["max"]
                    if lo and hi: hints.append(f"**{s}**: {lo}–{hi}")
                    elif lo and not hi: hints.append(f"**{s}**: ≥{lo}")
                    elif not lo and hi: hints.append(f"**{s}**: ≤{hi}")
                if hints: st.caption(f"Ranges ({unit}): " + " · ".join(hints))
                st.text_input(f"Performance value ({unit})", key=f"p2_{mk}_perf", placeholder=f"Enter a number ({unit})")
            else:
                options = ["— Select —"] + [mc["descriptors"][s] for s in ("1","2","3","4","5")]
                st.selectbox("Select performance level", options, key=f"p2_{mk}_perf")

        st.markdown("---")
        _,_,rc = st.columns([2,2,1])
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
            perf_val = st.session_state.get(f"p2_{mk}_perf","")
            score = compute_score(mk, perf_val)
            display_perf = perf_val if perf_val and perf_val != "— Select —" else ""
            if m["type"]=="quantitative" and display_perf:
                num = _safe_float(display_perf)
                if num is not None:
                    unit = m.get("unit","") or ""
                    if unit == "$": display_perf = f"${num:,.0f}"
                    elif unit == "%": display_perf = f"{num:g}%"
                    else: display_perf = f"{num:g} {unit}".strip()
            rows.append({"id":m["id"],"key":mk,"name":m["name"],"type":m["type"],"performance":display_perf,"score":score})
            if score is not None:
                total += score
                scored += 1
        st.session_state["_p2_results"] = {"partner_name":partner_name.strip(),"rows":rows,"total_score":total,"scored_count":scored,"max_possible":scored*5,"percentage":round(total/(scored*5)*100,1) if scored else 0}
        st.rerun()
