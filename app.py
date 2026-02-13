"""
ChannelPRO — Partner Revenue Optimizer
=======================================
Client Intake → Phase 1 (Scoring Criteria) → Phase 2 (Score a Partner)

Run:  streamlit run app.py
"""

import json, pathlib, re
import streamlit as st

# ═════════════════════════════════════════════════════════════════════════
# 0.  LOGO (base64-embedded The York Group logo)
# ═════════════════════════════════════════════════════════════════════════

YORK_LOGO_B64 = "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"

# ═════════════════════════════════════════════════════════════════════════
# 1.  METRIC DEFINITIONS
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
SCORE_COLORS = {1:"#dc4040",2:"#e8820c",3:"#d4a917",4:"#49a34f",5:"#1b6e23"}


# ═════════════════════════════════════════════════════════════════════════
# 2.  HELPERS
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
            crit[k] = {"name":m["name"],"type":"quantitative","format":m["format"],"unit":m["unit"],"direction":m["direction"],
                        "enabled":True,
                        "ranges":{s:{"min":m["defaults"][s]["min"],"max":m["defaults"][s]["max"]} for s in ("1","2","3","4","5")}}
        else:
            crit[k] = {"name":m["name"],"type":"qualitative","format":"descriptor_scale","unit":None,"direction":m["direction"],
                        "enabled":True,
                        "descriptors":{s:m["defaults"][s] for s in ("1","2","3","4","5")}}
    st.session_state["criteria"] = crit

def _save_criteria_from_form():
    crit = st.session_state["criteria"]
    for m in SCORECARD_METRICS:
        mk = m["key"]
        # enabled/disabled
        crit[mk]["enabled"] = st.session_state.get(f"p1_{mk}_enabled", True)
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
    if not crit.get("enabled", True): return None
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
    return SCORE_COLORS.get(score, "#999")

def _grade_label(pct):
    if pct >= 90: return "A","#1b6e23"
    if pct >= 80: return "B+","#49a34f"
    if pct >= 70: return "B","#6aab2e"
    if pct >= 60: return "C+","#d4a917"
    if pct >= 50: return "C","#e8820c"
    return "D","#dc4040"

def _get_enabled_metrics():
    """Return only metrics that are enabled in criteria."""
    crit = st.session_state.get("criteria", {})
    return [m for m in SCORECARD_METRICS if crit.get(m["key"], {}).get("enabled", True)]

def _get_partner_tiers():
    """Get partner tier list from client intake designations."""
    ci = st.session_state.get("client_info", {})
    raw = ci.get("partner_designations", "")
    if not raw: return []
    return [t.strip() for t in raw.split(",") if t.strip()]

def _render_logo():
    st.markdown(f'<img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;margin-bottom:8px;">', unsafe_allow_html=True)

def _render_brand_header():
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">
        <img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;border-radius:6px;">
        <div>
            <div style="font-size:1.6rem;font-weight:800;color:#1e2a3a;letter-spacing:-0.02em;">ChannelPRO</div>
            <div style="font-size:.92rem;color:#4a6a8f;font-weight:600;margin-top:-4px;">Partner Revenue Optimizer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# 3.  PAGE CONFIG & CSS
# ═════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="ChannelPRO — Partner Revenue Optimizer", page_icon="📋", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"] { background:#f3f5f9; font-family:'DM Sans',sans-serif; }
section[data-testid="stSidebar"] { background:linear-gradient(195deg,#162033,#1e2d45); }
section[data-testid="stSidebar"] * { color:#c4cfde !important; }
section[data-testid="stSidebar"] hr { border-color:#2a3d57 !important; }
.info-box { background:#f0f2f7; border-left:4px solid #2563eb; border-radius:8px;
    padding:22px 26px; margin:20px 0 28px; line-height:1.7; color:#2c3e56; font-size:.92rem; }
.info-box ol { margin:10px 0 10px 18px; padding:0; }
.mc { background:#fff; border:1px solid #e2e6ed; border-radius:14px;
      padding:20px 24px; margin-bottom:16px; box-shadow:0 1px 4px rgba(0,0,0,.03); }
.mc:hover { border-color:#b0bdd0; box-shadow:0 4px 16px rgba(0,0,0,.07); }
.mc-disabled { opacity:0.45; }
.mname { font-size:1.02rem; font-weight:700; color:#1e2a3a; }
.mexpl { font-size:.83rem; color:#5a6a7e; margin:2px 0 10px; line-height:1.45; }
.tag { font-size:.68rem; font-weight:700; padding:2px 9px; border-radius:20px;
       text-transform:uppercase; letter-spacing:.04em; display:inline-block; margin-left:6px; }
.tag-q { background:#dbe8ff; color:#1c5dbf; }
.tag-ql { background:#eedeff; color:#6b3fa0; }
.tag-hi { background:#e3f5e5; color:#2e7d32; }
.tag-lo { background:#fff3e0; color:#e65100; }
.tag-del { background:#fde8e8; color:#dc4040; }
.sb { display:inline-flex; align-items:center; justify-content:center;
      width:28px; height:28px; border-radius:8px; font-size:.78rem;
      font-weight:800; color:#fff; margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.sb1{background:#dc4040}.sb2{background:#e8820c}.sb3{background:#d4a917;color:#333!important}
.sb4{background:#49a34f}.sb5{background:#1b6e23}
.toast { background:#1b6e23; color:#fff; padding:.7rem 1.2rem; border-radius:10px;
         font-weight:600; text-align:center; margin-bottom:1rem; }
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
.sec-head { font-size:1.15rem; font-weight:800; color:#1e2a3a; margin:28px 0 12px;
            padding-bottom:8px; border-bottom:2px solid #e2e6ed; }
.partner-hdr { background:linear-gradient(135deg,#8b9bb8,#a5b3c9); color:#fff; padding:10px 18px;
               border-radius:10px 10px 0 0; font-weight:700; font-size:1rem; margin-bottom:0; }
.partner-box { background:#fff; border:1px solid #e2e6ed; border-top:none;
               border-radius:0 0 12px 12px; padding:20px 24px; margin-bottom:24px; }
.live-score { display:inline-flex; align-items:center; justify-content:center; width:44px; height:44px;
              border-radius:10px; font-size:1.2rem; font-weight:800; color:#fff;
              font-family:'JetBrains Mono',monospace; }
.hint-row { font-size:.78rem; color:#7a8a9e; font-family:'JetBrains Mono',monospace;
            margin:6px 0 10px; line-height:1.6; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# 4.  INIT STATE
# ═════════════════════════════════════════════════════════════════════════

_init_criteria_state()
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Client Intake"
if "client_info" not in st.session_state:
    if CLIENT_PATH.exists():
        try: st.session_state["client_info"] = json.loads(CLIENT_PATH.read_text())
        except Exception: st.session_state["client_info"] = {}
    else:
        st.session_state["client_info"] = {}


# ═════════════════════════════════════════════════════════════════════════
# 5.  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════

PAGES = ["Client Intake", "Phase 1 — Scoring Criteria", "Phase 2 — Score a Partner"]

with st.sidebar:
    _render_logo()
    st.markdown("**ChannelPRO** — Partner Revenue Optimizer")
    st.markdown("---")

    page = st.radio("Navigate", PAGES,
        index=PAGES.index(st.session_state["current_page"]) if st.session_state["current_page"] in PAGES else 0,
        key="nav_radio", label_visibility="collapsed")
    st.session_state["current_page"] = page
    st.markdown("---")

    if page != "Client Intake":
        cat_labels = ["All Metrics"] + [f"{c['icon']}  {c['label']}" for c in CATEGORIES]
        chosen_cat = st.radio("Category filter", cat_labels, index=0, label_visibility="collapsed")
    else:
        chosen_cat = "All Metrics"

    st.markdown("---")
    criteria_ready = SAVE_PATH.exists()
    if criteria_ready: st.success("✅ Criteria saved")
    else: st.info("ℹ️ Complete Phase 1 first")

    enabled = _get_enabled_metrics()
    quant_n = sum(1 for m in enabled if m["type"]=="quantitative")
    qual_n = len(enabled) - quant_n
    st.metric("Active Metrics", len(enabled))
    col_a, col_b = st.columns(2)
    col_a.metric("Quantitative", quant_n)
    col_b.metric("Qualitative", qual_n)

# Filter visible metrics
if chosen_cat == "All Metrics":
    visible_metrics = SCORECARD_METRICS
else:
    cat_name = chosen_cat.split("  ",1)[-1]
    cat_keys = next(c["keys"] for c in CATEGORIES if c["label"]==cat_name)
    visible_metrics = [METRICS_BY_KEY[k] for k in cat_keys]


# ═════════════════════════════════════════════════════════════════════════
# 6.  CLIENT INTAKE PAGE
# ═════════════════════════════════════════════════════════════════════════

if page == "Client Intake":
    _render_brand_header()

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

        st.markdown('<div class="sec-head">🏢 Client Business Information</div>', unsafe_allow_html=True)

        st.markdown("**What size company do you typically sell to?** *(Select no more than two)*")
        size_options = ["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]
        saved_sizes = ci.get("company_size", [])
        size_cols = st.columns(len(size_options))
        sizes_selected = []
        for i, opt in enumerate(size_options):
            with size_cols[i]:
                if st.checkbox(opt, value=opt in saved_sizes, key=f"ci_size_{i}"): sizes_selected.append(opt)

        st.markdown("**Are there specific verticals you sell to?**")
        vertical_options = ["Manufacturing","Automotive","Health care","Financial services","Retail","Government",
            "Education","Media and entertainment","Professional services","Life sciences, pharmaceuticals",
            "High-tech, electronics, communications, telecom","None - we have a horizontal solution"]
        saved_verts = ci.get("verticals", [])
        vert_cols = st.columns(3)
        verts_selected = []
        for i, opt in enumerate(vertical_options):
            with vert_cols[i % 3]:
                if st.checkbox(opt, value=opt in saved_verts, key=f"ci_vert_{i}"): verts_selected.append(opt)
        other_verts = st.text_input("Other verticals", value=ci.get("other_verticals",""), key="ci_other_verts")

        st.markdown("**How is the solution delivered?** *(Check all that apply)*")
        delivery_options = ["On-premise","SaaS/PaaS","IaaS/VM","As a device (hardware and software)"]
        saved_delivery = ci.get("solution_delivery", [])
        del_cols = st.columns(len(delivery_options))
        delivery_selected = []
        for i, opt in enumerate(delivery_options):
            with del_cols[i]:
                if st.checkbox(opt, value=opt in saved_delivery, key=f"ci_del_{i}"): delivery_selected.append(opt)

        st.markdown("**Average first-year transaction value** (not including services, maintenance)")
        txn_options = ["Under $1,000","$1,000-$10,000","$10,000-$50,000","$50,000-$100,000","More than $100,000"]
        saved_txn = ci.get("avg_transaction_value","")
        txn_value = st.radio("Select range", txn_options, index=txn_options.index(saved_txn) if saved_txn in txn_options else 0, key="ci_txn", horizontal=True)

        st.markdown("**Services as part of the transaction** (as % of software license/subscription)")
        svc_options = ["No services","<20%","20-50%","50-200%",">200%"]
        saved_svc = ci.get("services_pct","")
        svc_value = st.radio("Select range", svc_options, index=svc_options.index(saved_svc) if saved_svc in svc_options else 0, key="ci_svc", horizontal=True)
        svc_comments = st.text_input("Comments (services)", value=ci.get("services_comments",""), key="ci_svc_comments")

        st.markdown("**How many resellers/channel partners do you have?**")
        pc_opts = ["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]
        saved_pc = ci.get("partner_count","")
        partner_count = st.radio("Select range", pc_opts, index=pc_opts.index(saved_pc) if saved_pc in pc_opts else 0, key="ci_pc", horizontal=True)

        st.markdown("**Percentage of revenues from indirect channels**")
        ind_opts = ["<10%","10-30%","30-50%",">50%"]
        saved_ind = ci.get("indirect_revenue_pct","")
        indirect_pct = st.radio("Select range", ind_opts, index=ind_opts.index(saved_ind) if saved_ind in ind_opts else 0, key="ci_indirect", horizontal=True)

        st.markdown("**Discounts currently given to channel partners** *(Select all that apply)*")
        disc_options = ["<15%","15-30%","30-50%",">60%","Other"]
        saved_disc = ci.get("discounts", [])
        disc_cols = st.columns(len(disc_options))
        disc_selected = []
        for i, opt in enumerate(disc_options):
            with disc_cols[i]:
                if st.checkbox(opt, value=opt in saved_disc, key=f"ci_disc_{i}"): disc_selected.append(opt)

        st.markdown("**Partner designations**")
        partner_desig = st.text_input("Use comma-separated text, e.g. gold, silver, bronze",
            value=ci.get("partner_designations",""), key="ci_desig")

        st.markdown("---")
        col_l, col_r = st.columns([3,1])
        with col_r:
            intake_submitted = st.form_submit_button("Next →  Phase 1", use_container_width=True, type="primary")

    if intake_submitted:
        st.session_state["client_info"] = {
            "client_name":client_name,"project_manager":client_pm,"url":client_url,
            "city":client_city,"country":client_country,"email":client_email,"phone":client_phone,
            "company_size":sizes_selected,"verticals":verts_selected,"other_verticals":other_verts,
            "solution_delivery":delivery_selected,"avg_transaction_value":txn_value,
            "services_pct":svc_value,"services_comments":svc_comments,
            "partner_count":partner_count,"indirect_revenue_pct":indirect_pct,
            "discounts":disc_selected,"partner_designations":partner_desig,
        }
        CLIENT_PATH.write_text(json.dumps(st.session_state["client_info"], indent=2))
        st.session_state["_client_saved"] = True
        st.session_state["current_page"] = "Phase 1 — Scoring Criteria"
        st.rerun()

    # Download stored client data
    if CLIENT_PATH.exists():
        st.markdown("---")
        with st.expander("📊 Download stored client data"):
            raw = CLIENT_PATH.read_text()
            st.download_button("⬇️ Download client_info.json", raw, "client_info.json", "application/json")


# ═════════════════════════════════════════════════════════════════════════
# 7.  PHASE 1 — SCORING CRITERIA (with delete option)
# ═════════════════════════════════════════════════════════════════════════

elif page == "Phase 1 — Scoring Criteria":
    _render_brand_header()
    st.markdown("## Phase 1 — Define Scoring Criteria")
    st.markdown("Configure **1–5 scoring thresholds** for each metric. Use the ✅ toggle to include/exclude metrics from Phase 2 scoring.")

    if st.session_state.get("_p1_saved"):
        st.markdown('<div class="toast">✅ Criteria saved</div>', unsafe_allow_html=True)
        st.session_state["_p1_saved"] = False

    with st.form("phase1_form"):
        for m in visible_metrics:
            mk = m["key"]
            crit = st.session_state["criteria"][mk]
            is_q = m["type"]=="quantitative"
            is_enabled = crit.get("enabled", True)

            type_tag = '<span class="tag tag-q">Quantitative</span>' if is_q else '<span class="tag tag-ql">Qualitative</span>'
            dir_tag = f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
            del_tag = '' if is_enabled else '<span class="tag tag-del">EXCLUDED</span>'
            disabled_cls = "" if is_enabled else " mc-disabled"
            unit_d = f' ({m["unit"]})' if m.get("unit") else ""

            st.markdown(f'<div class="mc{disabled_cls}"><span class="mname">{m["id"]}. {m["name"]}</span>{type_tag}{dir_tag}{del_tag}<div class="mexpl">{m["explanation"]}</div></div>', unsafe_allow_html=True)

            # Enable/disable toggle
            st.checkbox("Include this metric in scoring", value=is_enabled, key=f"p1_{mk}_enabled")

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
            st.session_state["current_page"] = "Phase 2 — Score a Partner"
        st.rerun()

    if SAVE_PATH.exists():
        st.markdown("---")
        with st.expander("📄 Preview / Download scoring_criteria.json"):
            raw = SAVE_PATH.read_text()
            st.code(raw, language="json")
            st.download_button("⬇️ Download JSON", raw, "scoring_criteria.json", "application/json")


# ═════════════════════════════════════════════════════════════════════════
# 8.  PHASE 2 — SCORE A PARTNER (consolidated, live scoring)
# ═════════════════════════════════════════════════════════════════════════

else:
    _render_brand_header()
    st.markdown("## Phase 2 — Score a Partner")

    if not SAVE_PATH.exists():
        st.warning("⚠️ No scoring criteria found. Please complete **Phase 1** first and save criteria.")
        st.stop()

    # Reload criteria
    st.session_state["criteria"] = json.loads(SAVE_PATH.read_text())
    crit = st.session_state["criteria"]

    enabled_metrics = _get_enabled_metrics()
    max_score = len(enabled_metrics) * 5

    st.markdown(f"Enter partner performance data. Scores update **live** as you fill in values. Total out of **{max_score}** ({len(enabled_metrics)} metrics × 5).")

    # ── Partner Details Header ────────────────────────────────────────
    st.markdown('<div class="partner-hdr">Partner details</div>', unsafe_allow_html=True)

    tiers = _get_partner_tiers()
    tier_options = ["Please choose..."] + tiers if tiers else ["Please choose...", "(Set tiers in Client Intake)"]

    with st.container():
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            partner_name = st.text_input("Partner company name", key="p2_partner_name", placeholder="e.g. ABC reseller")
        with p_col2:
            partner_year = st.text_input("Year become partner", key="p2_partner_year", placeholder="e.g. 2020")
        with p_col3:
            partner_tier = st.selectbox("Tier", tier_options, key="p2_partner_tier")

        p_col4, p_col5 = st.columns(2)
        with p_col4:
            partner_city = st.text_input("City", key="p2_partner_city", placeholder="e.g. Paris")
        with p_col5:
            partner_country = st.text_input("Country", key="p2_partner_country", placeholder="e.g. France")

    st.markdown("---")

    # ── Filter for enabled + category ─────────────────────────────────
    if chosen_cat == "All Metrics":
        visible_enabled = enabled_metrics
    else:
        cat_name = chosen_cat.split("  ",1)[-1]
        cat_keys = next(c["keys"] for c in CATEGORIES if c["label"]==cat_name)
        visible_enabled = [m for m in enabled_metrics if m["key"] in cat_keys]

    # ── Live scoring for each metric ──────────────────────────────────
    all_scores = {}

    for m in visible_enabled:
        mk = m["key"]
        mc = crit[mk]
        is_q = m["type"]=="quantitative"

        type_tag = '<span class="tag tag-q">Quantitative</span>' if is_q else '<span class="tag tag-ql">Qualitative</span>'
        dir_tag = f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'

        st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{type_tag}{dir_tag}<div class="mexpl">{m["explanation"]}</div></div>', unsafe_allow_html=True)

        if is_q:
            # Show ranges as reference
            unit = mc.get("unit","") or ""
            hints = []
            for s in ("1","2","3","4","5"):
                r = mc["ranges"][s]; lo, hi = r["min"], r["max"]
                if lo and hi: hints.append(f"<b>{s}</b>: {lo}–{hi}")
                elif lo and not hi: hints.append(f"<b>{s}</b>: ≥{lo}")
                elif not lo and hi: hints.append(f"<b>{s}</b>: ≤{hi}")
            if hints:
                st.markdown(f'<div class="hint-row">Ranges ({unit}): {" &nbsp;·&nbsp; ".join(hints)}</div>', unsafe_allow_html=True)

            inp_col, score_col = st.columns([4, 1])
            with inp_col:
                perf_val = st.text_input(f"Performance ({unit})", key=f"p2_{mk}_perf", placeholder=f"Enter a number ({unit})", label_visibility="collapsed")
            sc = compute_score(mk, perf_val)
        else:
            # Show descriptors as selectable options
            options = ["— Select —"] + [f"({s}) {mc['descriptors'][s]}" for s in ("1","2","3","4","5")]
            inp_col, score_col = st.columns([4, 1])
            with inp_col:
                perf_val = st.selectbox("Select performance level", options, key=f"p2_{mk}_perf", label_visibility="collapsed")
            # Extract the descriptor from selection to match
            if perf_val and perf_val != "— Select —":
                # Strip the (N) prefix to get the raw descriptor
                raw_desc = re.sub(r"^\(\d\)\s*", "", perf_val)
                sc = compute_score(mk, raw_desc)
            else:
                sc = None

        with score_col:
            if sc is not None:
                sc_color = _score_color(sc)
                st.markdown(f'<div class="live-score" style="background:{sc_color};">{sc}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="live-score" style="background:#ccc;">—</div>', unsafe_allow_html=True)

        all_scores[mk] = sc

    # ── Live Summary ──────────────────────────────────────────────────
    st.markdown("---")

    # Compute for ALL enabled metrics (not just visible category)
    full_scores = {}
    for m in enabled_metrics:
        mk = m["key"]
        perf = st.session_state.get(f"p2_{mk}_perf", "")
        if not perf or perf == "— Select —":
            full_scores[mk] = None
        else:
            mc = crit[mk]
            if m["type"] == "qualitative" and perf.startswith("("):
                raw_desc = re.sub(r"^\(\d\)\s*", "", perf)
                full_scores[mk] = compute_score(mk, raw_desc)
            else:
                full_scores[mk] = compute_score(mk, perf)

    scored_items = {k:v for k,v in full_scores.items() if v is not None}
    total = sum(scored_items.values())
    scored_n = len(scored_items)
    max_possible = scored_n * 5
    pct = (total / max_possible * 100) if max_possible else 0
    grade_l, grade_c = _grade_label(pct)

    p_name = st.session_state.get("p2_partner_name", "Partner")
    if not p_name: p_name = "Partner"

    st.markdown(f"### Live Score Summary — {p_name}")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f'<div class="sum-card"><div class="sum-big">{total}</div><div class="sum-lbl">Total Score</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sum-card"><div class="sum-big">{scored_n}/{len(enabled_metrics)}</div><div class="sum-lbl">Metrics Scored</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="sum-card"><div class="sum-big">{pct:.1f}%</div><div class="sum-lbl">Percentage</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:{grade_c}">{grade_l}</div><div class="sum-lbl">Grade</div></div>', unsafe_allow_html=True)

    # ── Results Table ─────────────────────────────────────────────────
    if scored_n > 0:
        tbl_rows = ""
        for m in enabled_metrics:
            mk = m["key"]
            sc = full_scores.get(mk)
            perf_raw = st.session_state.get(f"p2_{mk}_perf", "")
            if perf_raw == "— Select —": perf_raw = ""

            # Format performance display
            disp = perf_raw
            if m["type"]=="quantitative" and perf_raw:
                num = _safe_float(perf_raw)
                if num is not None:
                    u = m.get("unit","") or ""
                    if u == "$": disp = f"${num:,.0f}"
                    elif u == "%": disp = f"{num:g}%"
                    else: disp = f"{num:g} {u}".strip()

            sc_color = _score_color(sc) if sc else "#999"
            sc_display = f'<span class="score-pill" style="background:{sc_color}">{sc}</span>' if sc else '<span style="color:#999">—</span>'
            perf_display = disp if disp else '<span style="color:#999">—</span>'
            type_tag = '<span class="tag tag-q">Q</span>' if m["type"]=="quantitative" else '<span class="tag tag-ql">QL</span>'
            tbl_rows += f'<tr><td>{m["id"]}</td><td>{m["name"]} {type_tag}</td><td>{perf_display}</td><td>{sc_display}</td></tr>'

        st.markdown(f"""<table class="res-tbl">
        <thead><tr><th>#</th><th>Metric</th><th>Performance</th><th>Score</th></tr></thead>
        <tbody>{tbl_rows}
        <tr style="background:#f0f2f7;font-weight:700;"><td colspan="3" style="text-align:right;">TOTAL</td>
        <td><span class="score-pill" style="background:#1e2a3a">{total}/{max_possible}</span> ({pct:.1f}%)</td></tr></tbody></table>""", unsafe_allow_html=True)

        # Download results
        results_data = {
            "partner_name": p_name,
            "partner_year": st.session_state.get("p2_partner_year",""),
            "partner_tier": st.session_state.get("p2_partner_tier",""),
            "partner_city": st.session_state.get("p2_partner_city",""),
            "partner_country": st.session_state.get("p2_partner_country",""),
            "total_score": total,
            "scored_count": scored_n,
            "max_possible": max_possible,
            "percentage": round(pct, 1),
            "metrics": [{"id":m["id"],"name":m["name"],"performance":st.session_state.get(f"p2_{m['key']}_perf",""),"score":full_scores.get(m["key"])} for m in enabled_metrics],
        }
        st.download_button("⬇️ Download Results JSON", json.dumps(results_data, indent=2),
            f"{p_name.replace(' ','_')}_scorecard.json", "application/json")
