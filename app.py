"""
ChannelPRO — Partner Revenue Optimizer
=======================================
Client Intake → Step 1 (Scoring Criteria) → Step 2 (Score a Partner) → Step 3 (Partner Assessment)
Run:  streamlit run app.py
"""
import csv, io, json, pathlib, re
import streamlit as st

YORK_LOGO_B64 = "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"

# ═════════════════════════════════════════════════════════════════════════
# 1. METRICS
# ═════════════════════════════════════════════════════════════════════════
SCORECARD_METRICS = [
    {"id":1,"key":"annual_revenues","name":"Annual revenues for vendor","explanation":"Total amount received from the partner, net of discounts/margins.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"50000"},"2":{"min":"50001","max":"150000"},"3":{"min":"150001","max":"350000"},"4":{"min":"350001","max":"750000"},"5":{"min":"750001","max":""}}},
    {"id":2,"key":"yoy_revenue_growth","name":"Year-on-year revenue growth","explanation":"% increase/decrease in revenues, past 12 mo over previous 12 mo.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"10"},"3":{"min":"10","max":"20"},"4":{"min":"20","max":"35"},"5":{"min":"35","max":""}}},
    {"id":3,"key":"net_new_logo_revenues","name":"Net-new logo revenues","explanation":"Revenues from selling to new customers.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"10000"},"2":{"min":"10001","max":"50000"},"3":{"min":"50001","max":"150000"},"4":{"min":"150001","max":"350000"},"5":{"min":"350001","max":""}}},
    {"id":4,"key":"pct_revenues_saas","name":"% of vendor revenues from SaaS","explanation":"Transformation to SaaS/recurring revenues.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":5,"key":"net_revenue_expansion","name":"Net revenue expansion","explanation":"Growth in revenues for existing customers.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"","max":"0"},"2":{"min":"0","max":"5"},"3":{"min":"5","max":"15"},"4":{"min":"15","max":"25"},"5":{"min":"25","max":""}}},
    {"id":6,"key":"total_revenues","name":"Total revenues (if available)","explanation":"Overall revenues including all products and services.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Revenue & Growth","defaults":{"1":{"min":"0","max":"1000000"},"2":{"min":"1000001","max":"5000000"},"3":{"min":"5000001","max":"20000000"},"4":{"min":"20000001","max":"100000000"},"5":{"min":"100000001","max":""}}},
    {"id":7,"key":"average_deal_size","name":"Average deal size","explanation":"Average annualized subscription/license value.","type":"quantitative","unit":"$","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5000"},"2":{"min":"5001","max":"15000"},"3":{"min":"15001","max":"40000"},"4":{"min":"40001","max":"100000"},"5":{"min":"100001","max":""}}},
    {"id":8,"key":"avg_time_to_close","name":"Average time to close","explanation":"Deal registration to signed subscription/EULA.","type":"quantitative","unit":"days","direction":"lower_is_better","cat":"Sales Performance","defaults":{"1":{"min":"181","max":""},"2":{"min":"121","max":"180"},"3":{"min":"61","max":"120"},"4":{"min":"31","max":"60"},"5":{"min":"0","max":"30"}}},
    {"id":9,"key":"registered_deals","name":"Registered deals","explanation":"Number of deals registered with vendor.","type":"quantitative","unit":"count","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"6","max":"15"},"3":{"min":"16","max":"30"},"4":{"min":"31","max":"60"},"5":{"min":"61","max":""}}},
    {"id":10,"key":"win_loss_ratio","name":"Win/loss ratio","explanation":"% of registered deals that closed.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"40"},"4":{"min":"40","max":"60"},"5":{"min":"60","max":"100"}}},
    {"id":11,"key":"partner_generated_opps_pct","name":"Partner Generated Opps as % of Pipeline","explanation":"Partner-generated vs. vendor leads.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":{"min":"0","max":"10"},"2":{"min":"10","max":"25"},"3":{"min":"25","max":"50"},"4":{"min":"50","max":"75"},"5":{"min":"75","max":"100"}}},
    {"id":12,"key":"frequency_of_business","name":"Frequency of business","explanation":"Steady flow or seasonal?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Sales Performance","defaults":{"1":"Sporadic — 1-2 transactions/year","2":"Seasonal — clustered in 1-2 quarters","3":"Moderate — activity most quarters","4":"Consistent — monthly or near-monthly","5":"Highly active — continuous deal flow"}},
    {"id":13,"key":"renewal_rate","name":"Renewal rate","explanation":"% of subscriptions renewed.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":{"min":"0","max":"60"},"2":{"min":"60","max":"75"},"3":{"min":"75","max":"85"},"4":{"min":"85","max":"93"},"5":{"min":"93","max":"100"}}},
    {"id":14,"key":"customer_satisfaction","name":"Customer satisfaction","explanation":"NPS or satisfaction measurement.","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"No measurement; frequent complaints","2":"Anecdotal only; some dissatisfaction","3":"Measured informally; average","4":"Formal NPS/CSAT; consistently positive","5":"Industry-leading; referenceable customers"}},
    {"id":15,"key":"communication_with_vendor","name":"Communication with vendor","explanation":"Quality of communications — calls, QBRs, visits.","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Retention & Satisfaction","defaults":{"1":"Unresponsive — hard to reach","2":"Reactive only","3":"Periodic — monthly calls, no QBR","4":"Strong — regular cadence, QBRs","5":"Exemplary — weekly touchpoints, exec visits"}},
    {"id":16,"key":"mdf_utilization_rate","name":"MDF utilization rate","explanation":"Using vendor-sponsored marketing funds?","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"20"},"2":{"min":"20","max":"40"},"3":{"min":"40","max":"60"},"4":{"min":"60","max":"80"},"5":{"min":"80","max":"100"}}},
    {"id":17,"key":"quality_of_sales_org","name":"Quality of sales organization","explanation":"Do they need more guidance?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Weak — no dedicated reps","2":"Below average — lack product knowledge","3":"Adequate — average metrics","4":"Strong — good pipeline management","5":"Excellent — top-tier, consistently high"}},
    {"id":18,"key":"vendor_certifications","name":"Vendor certification(s)","explanation":"Investing in your technology?","type":"quantitative","unit":"certs","direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":{"min":"0","max":"0"},"2":{"min":"1","max":"2"},"3":{"min":"3","max":"5"},"4":{"min":"6","max":"10"},"5":{"min":"11","max":""}}},
    {"id":19,"key":"sales_support_calls","name":"Sales support calls received","explanation":"Big pipeline or can't sell?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive — lack of knowledge","2":"Frequent routine questions","3":"Moderate — mixed","4":"Mostly deal-strategy-driven","5":"Rare — complex high-value only"}},
    {"id":20,"key":"tech_support_calls","name":"Tech support calls received","explanation":"Lack of training?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Enablement & Support","defaults":{"1":"Excessive — training gaps","2":"Frequent — certs should cover","3":"Average — occasional escalations","4":"Low — complex edge cases","5":"Minimal — self-sufficient"}},
    {"id":21,"key":"dedication_vs_competitive","name":"Dedication vs. competitive products","explanation":"Strategic vendor or afterthought?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Sells competitor as primary","2":"Competitor default; you by request","3":"Sells both equally","4":"You preferred; competitor secondary","5":"Exclusively sells your solution"}},
    {"id":22,"key":"dedication_vs_other_vendors","name":"Dedication vs. other vendors","explanation":"% of business your solution represents.","type":"quantitative","unit":"%","direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":{"min":"0","max":"5"},"2":{"min":"5","max":"15"},"3":{"min":"15","max":"30"},"4":{"min":"30","max":"50"},"5":{"min":"50","max":"100"}}},
    {"id":23,"key":"geographical_coverage","name":"Geographical market coverage","explanation":"Right-sized territory?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"Very limited local presence","2":"Small territory; gaps","3":"Adequate regional coverage","4":"Strong multi-region, aligned","5":"National/intl or dominant"}},
    {"id":24,"key":"vertical_coverage","name":"Vertical market coverage","explanation":"Specialize in verticals?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Strategic Fit","defaults":{"1":"No vertical focus","2":"Emerging in 1 vertical","3":"Established in 1-2 verticals","4":"Strong domain expertise","5":"Dominant authority; deep base"}},
    {"id":25,"key":"quality_of_management","name":"Quality of management","explanation":"How well do they run their business?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Poor — disorganized","2":"Below avg — reactive","3":"Adequate — competent","4":"Strong — proactive, clear strategy","5":"Exceptional — visionary leadership"}},
    {"id":26,"key":"known_litigation","name":"Known litigation (No=5, Yes=1)","explanation":"Involved in lawsuits?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Active major litigation","2":"Material financial exposure","3":"Minor pending disputes","4":"Past litigation resolved","5":"No known litigation"}},
    {"id":27,"key":"export_control_ip","name":"Export control & IP protection","explanation":"Complying with provisions?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Known violations","2":"Gaps; no remediation","3":"Generally compliant","4":"Fully compliant; proactive","5":"Best-in-class compliance"}},
    {"id":28,"key":"financial_strength","name":"Financial strength","explanation":"Cash-flow struggles or strong margins?","type":"qualitative","unit":None,"direction":"higher_is_better","cat":"Risk & Governance","defaults":{"1":"Severe cash-flow issues","2":"Thin margins; credit concerns","3":"Stable but modest","4":"Healthy margins; consistent profit","5":"Very strong; well-capitalized"}},
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
ALL_PARTNERS_CSV = pathlib.Path("all_partners.csv")
SC = {1:"#dc4040",2:"#e8820c",3:"#d4a917",4:"#49a34f",5:"#1b6e23"}

# ═════════════════════════════════════════════════════════════════════════
# 2. HELPERS
# ═════════════════════════════════════════════════════════════════════════
def _sf(val):
    if val is None: return None
    c = re.sub(r"[,$%\s]","",str(val).strip())
    if c == "": return None
    try: return float(c)
    except ValueError: return None

def _init_criteria():
    if "criteria" in st.session_state: return
    if SAVE_PATH.exists():
        try: st.session_state["criteria"]=json.loads(SAVE_PATH.read_text()); return
        except Exception: pass
    cr={}
    for m in SCORECARD_METRICS:
        k=m["key"]
        if m["type"]=="quantitative":
            cr[k]={"name":m["name"],"type":"quantitative","unit":m["unit"],"direction":m["direction"],"enabled":True,
                    "ranges":{s:{"min":m["defaults"][s]["min"],"max":m["defaults"][s]["max"]} for s in("1","2","3","4","5")}}
        else:
            cr[k]={"name":m["name"],"type":"qualitative","unit":None,"direction":m["direction"],"enabled":True,
                    "descriptors":{s:m["defaults"][s] for s in("1","2","3","4","5")}}
    st.session_state["criteria"]=cr

def _save_criteria():
    cr=st.session_state["criteria"]
    for m in SCORECARD_METRICS:
        mk=m["key"]; cr[mk]["enabled"]=st.session_state.get(f"p1_{mk}_en",True)
        if m["type"]=="quantitative":
            for s in("1","2","3","4","5"):
                cr[mk]["ranges"][s]["min"]=st.session_state.get(f"p1_{mk}_s{s}_min","")
                cr[mk]["ranges"][s]["max"]=st.session_state.get(f"p1_{mk}_s{s}_max","")
        else:
            for s in("1","2","3","4","5"):
                cr[mk]["descriptors"][s]=st.session_state.get(f"p1_{mk}_s{s}_desc","")
    SAVE_PATH.write_text(json.dumps(cr,indent=2))

def score(mk,val):
    cr=st.session_state["criteria"].get(mk)
    if not cr or not cr.get("enabled",True): return None
    if cr["type"]=="quantitative":
        v=_sf(val)
        if v is None: return None
        for s in("5","4","3","2","1"):
            r=cr["ranges"][s]; lo,hi=_sf(r["min"]),_sf(r["max"])
            if lo is not None and hi is not None and lo<=v<=hi: return int(s)
            if lo is not None and hi is None and v>=lo: return int(s)
            if lo is None and hi is not None and v<=hi: return int(s)
        return 1
    else:
        if not val or val=="— Select —": return None
        for s in("1","2","3","4","5"):
            if cr["descriptors"][s]==val: return int(s)
        return None

def _enabled():
    cr=st.session_state.get("criteria",{})
    return [m for m in SCORECARD_METRICS if cr.get(m["key"],{}).get("enabled",True)]

def _tiers():
    raw=st.session_state.get("client_info",{}).get("partner_designations","")
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []

def _grade(pct):
    if pct>=90: return "A","#1b6e23"
    if pct>=80: return "B+","#49a34f"
    if pct>=70: return "B","#6aab2e"
    if pct>=60: return "C+","#d4a917"
    if pct>=50: return "C","#e8820c"
    return "D","#dc4040"

def _logo():
    st.markdown(f'<img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;margin-bottom:8px;">',unsafe_allow_html=True)

def _brand():
    st.markdown(f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;"><img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;border-radius:6px;"><div><div style="font-size:1.6rem;font-weight:800;color:#1e2a3a;">ChannelPRO</div><div style="font-size:.92rem;color:#4a6a8f;font-weight:600;margin-top:-4px;">Partner Revenue Optimizer</div></div></div>',unsafe_allow_html=True)

def _append_partner_csv(row_dict):
    """Append a partner's scores to the cumulative CSV."""
    em = _enabled()
    fieldnames = ["partner_name","partner_year","partner_tier","partner_city","partner_country"]
    fieldnames += [m["key"] for m in em]
    fieldnames += ["total_score","max_possible","percentage"]
    exists = ALL_PARTNERS_CSV.exists()
    with open(ALL_PARTNERS_CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row_dict)

def _load_all_partners():
    """Load all submitted partners from CSV."""
    if not ALL_PARTNERS_CSV.exists(): return []
    rows = []
    with open(ALL_PARTNERS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def _generate_assessment_xlsx(partners, enabled_metrics):
    """Generate an XLSX in memory with heat-map colors."""
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    except ImportError:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Partner Assessment"

    fills = {
        1: PatternFill(start_color="FA7A7A", end_color="FA7A7A", fill_type="solid"),
        2: PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid"),
        3: PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid"),
        4: PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
        5: PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
    }
    hdr_fill = PatternFill(start_color="1E2A3A", end_color="1E2A3A", fill_type="solid")
    hdr_font = Font(color="FFFFFF", bold=True, size=10)
    border = Border(
        left=Side(style="thin", color="CCCCCC"), right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"), bottom=Side(style="thin", color="CCCCCC"))

    # Headers
    headers = ["Rank", "Partner Name", "Tier", "City", "Country"]
    headers += [m["name"] for m in enabled_metrics]
    headers += ["Total", "%"]

    for c, h in enumerate(headers, 1):
        cell = ws.cell(1, c, h)
        cell.fill = hdr_fill; cell.font = hdr_font; cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = border
        ws.column_dimensions[cell.column_letter].width = 14 if c > 5 else 18

    # Sort partners by total descending
    def sort_key(p):
        try: return -int(p.get("total_score", 0))
        except: return 0
    partners_sorted = sorted(partners, key=sort_key)

    for ri, p in enumerate(partners_sorted, 2):
        ws.cell(ri, 1, ri - 1).border = border
        ws.cell(ri, 1, ri - 1).alignment = Alignment(horizontal="center")
        ws.cell(ri, 2, p.get("partner_name", "")).border = border
        ws.cell(ri, 3, p.get("partner_tier", "")).border = border
        ws.cell(ri, 4, p.get("partner_city", "")).border = border
        ws.cell(ri, 5, p.get("partner_country", "")).border = border

        for ci, m in enumerate(enabled_metrics, 6):
            raw = p.get(m["key"], "")
            try:
                v = int(raw)
            except (ValueError, TypeError):
                v = None
            cell = ws.cell(ri, ci)
            cell.border = border
            cell.alignment = Alignment(horizontal="center")
            if v and 1 <= v <= 5:
                cell.value = v
                cell.fill = fills[v]
                cell.font = Font(bold=True)

        tc = len(enabled_metrics) + 6
        try:
            total_val = int(p.get("total_score", 0))
        except:
            total_val = 0
        ws.cell(ri, tc, total_val).border = border
        ws.cell(ri, tc).font = Font(bold=True)
        ws.cell(ri, tc).alignment = Alignment(horizontal="center")
        try:
            pct_val = float(p.get("percentage", 0))
        except:
            pct_val = 0
        pct_cell = ws.cell(ri, tc + 1)
        pct_cell.value = pct_val / 100
        pct_cell.number_format = "0.0%"
        pct_cell.border = border
        pct_cell.alignment = Alignment(horizontal="center")
        pct_cell.font = Font(bold=True)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════
# 3. PAGE CONFIG & CSS
# ═════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="ChannelPRO — Partner Revenue Optimizer", page_icon="📋", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"]{background:#f3f5f9;font-family:'DM Sans',sans-serif}
section[data-testid="stSidebar"]{background:linear-gradient(195deg,#162033,#1e2d45)}
section[data-testid="stSidebar"] *{color:#c4cfde!important}
section[data-testid="stSidebar"] hr{border-color:#2a3d57!important}
.info-box{background:#f0f2f7;border-left:4px solid #2563eb;border-radius:8px;padding:22px 26px;margin:20px 0 28px;line-height:1.7;color:#2c3e56;font-size:.92rem}
.info-box ol{margin:10px 0 10px 18px;padding:0}
.mc{background:#fff;border:1px solid #e2e6ed;border-radius:14px;padding:20px 24px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.mc:hover{border-color:#b0bdd0;box-shadow:0 4px 16px rgba(0,0,0,.07)}
.mc-off{opacity:.45}
.mname{font-size:1.02rem;font-weight:700;color:#1e2a3a}
.mexpl{font-size:.83rem;color:#5a6a7e;margin:2px 0 10px;line-height:1.45}
.tag{font-size:.68rem;font-weight:700;padding:2px 9px;border-radius:20px;text-transform:uppercase;letter-spacing:.04em;display:inline-block;margin-left:6px}
.tag-q{background:#dbe8ff;color:#1c5dbf}.tag-ql{background:#eedeff;color:#6b3fa0}
.tag-hi{background:#e3f5e5;color:#2e7d32}.tag-lo{background:#fff3e0;color:#e65100}
.tag-del{background:#fde8e8;color:#dc4040}
.sb{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;font-size:.78rem;font-weight:800;color:#fff;margin-bottom:4px;font-family:'JetBrains Mono',monospace}
.sb1{background:#dc4040}.sb2{background:#e8820c}.sb3{background:#d4a917;color:#333!important}.sb4{background:#49a34f}.sb5{background:#1b6e23}
.toast{background:#1b6e23;color:#fff;padding:.7rem 1.2rem;border-radius:10px;font-weight:600;text-align:center;margin-bottom:1rem}
.sum-card{background:linear-gradient(135deg,#1e2a3a,#2c3e56);border-radius:14px;padding:22px 24px;color:#fff;text-align:center}
.sum-big{font-size:2.4rem;font-weight:800;font-family:'JetBrains Mono',monospace}
.sum-lbl{font-size:.75rem;opacity:.7;text-transform:uppercase;letter-spacing:.06em;margin-top:2px}
.sec-head{font-size:1.15rem;font-weight:800;color:#1e2a3a;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e2e6ed}
.partner-hdr{background:linear-gradient(135deg,#8b9bb8,#a5b3c9);color:#fff;padding:10px 18px;border-radius:10px 10px 0 0;font-weight:700;font-size:1rem}
.live-score{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:10px;font-size:1.2rem;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace}
.hint-row{font-size:.78rem;color:#7a8a9e;font-family:'JetBrains Mono',monospace;margin:6px 0 10px;line-height:1.6}
/* Darker input fields */
[data-testid="stAppViewContainer"] input[type="text"],
[data-testid="stAppViewContainer"] textarea {
    background: #e8ebf1 !important; border: 1.5px solid #b0bdd0 !important;
}
[data-testid="stAppViewContainer"] input[type="text"]:focus,
[data-testid="stAppViewContainer"] textarea:focus {
    background: #fff !important; border-color: #2563eb !important;
}
/* Heat-map table */
.hm-tbl{width:100%;border-collapse:collapse;font-size:.82rem;background:#fff;margin:1rem 0}
.hm-tbl th{background:#1e2a3a;color:#fff;padding:8px 6px;text-align:center;font-weight:700;font-size:.72rem;text-transform:uppercase;white-space:nowrap;border:1px solid #2a3d57}
.hm-tbl td{padding:6px;text-align:center;border:1px solid #e2e6ed;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:.82rem}
.hm-tbl tr:hover td{filter:brightness(0.95)}
.hm1{background:#FA7A7A;color:#fff}.hm2{background:#FFFFCC;color:#333}.hm3{background:#FFFFCC;color:#333}
.hm4{background:#C6EFCE;color:#1b6e23}.hm5{background:#C6EFCE;color:#1b6e23}
.hm-total{background:#1e2a3a;color:#fff;font-weight:800}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════
# 4. INIT
# ═════════════════════════════════════════════════════════════════════════
_init_criteria()
if "current_page" not in st.session_state: st.session_state["current_page"]="Client Intake"
if "client_info" not in st.session_state:
    if CLIENT_PATH.exists():
        try: st.session_state["client_info"]=json.loads(CLIENT_PATH.read_text())
        except: st.session_state["client_info"]={}
    else: st.session_state["client_info"]={}

PAGES=["Client Intake","Step 1 — Scoring Criteria","Step 2 — Score a Partner","Step 3 — Partner Assessment"]

# ═════════════════════════════════════════════════════════════════════════
# 5. SIDEBAR
# ═════════════════════════════════════════════════════════════════════════
with st.sidebar:
    _logo()
    st.markdown("**ChannelPRO** — Partner Revenue Optimizer")
    st.markdown("---")
    page=st.radio("Navigate",PAGES,
        index=PAGES.index(st.session_state["current_page"]) if st.session_state["current_page"] in PAGES else 0,
        key="nav_radio",label_visibility="collapsed")
    st.session_state["current_page"]=page
    st.markdown("---")
    if page not in ("Client Intake","Step 3 — Partner Assessment"):
        cat_labels=["All Metrics"]+[f"{c['icon']}  {c['label']}" for c in CATEGORIES]
        chosen_cat=st.radio("Category",cat_labels,index=0,label_visibility="collapsed")
    else: chosen_cat="All Metrics"
    st.markdown("---")
    if SAVE_PATH.exists(): st.success("✅ Criteria saved")
    else: st.info("ℹ️ Complete Step 1 first")
    en=_enabled()
    st.metric("Active Metrics",len(en))
    # Partner count
    partners = _load_all_partners()
    st.metric("Partners Scored", len(partners))

if chosen_cat=="All Metrics": visible_metrics=SCORECARD_METRICS
else:
    cn=chosen_cat.split("  ",1)[-1]
    ck=next(c["keys"] for c in CATEGORIES if c["label"]==cn)
    visible_metrics=[METRICS_BY_KEY[k] for k in ck]

# ═════════════════════════════════════════════════════════════════════════
# 6. CLIENT INTAKE
# ═════════════════════════════════════════════════════════════════════════
if page=="Client Intake":
    _brand()
    st.markdown("""<div class="info-box">
    The <b>Partner Revenue Optimizer</b> is a structured process that will:
    <ol><li>Right-size the margins you provide to your partners, freeing up significant cash flow and revenues for you; and</li>
    <li>Lay the foundation for targeted partner marketing programs to drive more revenues from new and existing partners.</li></ol>
    <p>An experienced channel consultant from <b>The York Group</b> will guide you through the process. Some metrics will be readily available from your systems, while others will be more subjective. It is likely that some are not currently tracked — that is OK.</p>
    <p>Each metric is rated <b>1–5</b> (5 = best). Scores will be used to review each partner and feed into a heat map of all partners across all metrics.</p>
    </div>""",unsafe_allow_html=True)

    if st.session_state.get("_ci_saved"):
        st.markdown('<div class="toast">✅ Client information saved</div>',unsafe_allow_html=True)
        st.session_state["_ci_saved"]=False

    ci=st.session_state["client_info"]
    with st.form("ci_form"):
        st.markdown('<div class="sec-head">📇 Client Contact Information</div>',unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            ci_name=st.text_input("Client name",value=ci.get("client_name",""),key="ci_name")
            ci_url=st.text_input("URL",value=ci.get("url",""),key="ci_url")
            ci_country=st.text_input("Country",value=ci.get("country",""),key="ci_country")
            ci_phone=st.text_input("Primary phone",value=ci.get("phone",""),key="ci_phone")
        with c2:
            ci_pm=st.text_input("Client project manager",value=ci.get("project_manager",""),key="ci_pm")
            ci_city=st.text_input("City",value=ci.get("city",""),key="ci_city")
            ci_email=st.text_input("Primary contact email",value=ci.get("email",""),key="ci_email")

        st.markdown('<div class="sec-head">🏢 Client Business Information</div>',unsafe_allow_html=True)

        st.markdown("**What size company do you typically sell to?** *(Select no more than two)*")
        sz_opts=["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]
        saved_sz=ci.get("company_size",[])
        sz_cols=st.columns(len(sz_opts)); sz_sel=[]
        for i,o in enumerate(sz_opts):
            with sz_cols[i]:
                if st.checkbox(o,value=o in saved_sz,key=f"ci_sz_{i}"): sz_sel.append(o)

        st.markdown("**Verticals you sell to?**")
        v_opts=["Manufacturing","Automotive","Health care","Financial services","Retail","Government","Education","Media and entertainment","Professional services","Life sciences, pharmaceuticals","High-tech, electronics, communications, telecom","None - horizontal solution"]
        saved_v=ci.get("verticals",[])
        vc=st.columns(3); v_sel=[]
        for i,o in enumerate(v_opts):
            with vc[i%3]:
                if st.checkbox(o,value=o in saved_v,key=f"ci_v_{i}"): v_sel.append(o)
        other_v=st.text_input("Other verticals",value=ci.get("other_verticals",""),key="ci_ov")

        st.markdown("**Solution delivery** *(Check all that apply)*")
        d_opts=["On-premise","SaaS/PaaS","IaaS/VM","Device (HW+SW)"]
        saved_d=ci.get("solution_delivery",[])
        dc=st.columns(len(d_opts)); d_sel=[]
        for i,o in enumerate(d_opts):
            with dc[i]:
                if st.checkbox(o,value=o in saved_d,key=f"ci_d_{i}"): d_sel.append(o)

        st.markdown("**Average first-year transaction value** (solution only, excluding services)")
        t_opts=["Under $1,000","$1,000–$10,000","$10,000–$50,000","$50,000–$100,000","More than $100,000"]
        saved_t=ci.get("avg_transaction_value","")
        txn=st.radio("Range",t_opts,index=t_opts.index(saved_t) if saved_t in t_opts else 0,key="ci_txn",horizontal=True)

        st.markdown("**Services as % of license/subscription**")
        s_opts=["No services","<20%","20–50%","50–200%",">200%"]
        saved_s=ci.get("services_pct","")
        svc=st.radio("Range",s_opts,index=s_opts.index(saved_s) if saved_s in s_opts else 0,key="ci_svc",horizontal=True)
        svc_c=st.text_input("Comments",value=ci.get("services_comments",""),key="ci_svc_c")

        st.markdown("**How many resellers/channel partners?**")
        p_opts=["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]
        saved_p=ci.get("partner_count","")
        pc=st.radio("Range",p_opts,index=p_opts.index(saved_p) if saved_p in p_opts else 0,key="ci_pc",horizontal=True)

        st.markdown("**% of revenues from indirect channels**")
        i_opts=["<10%","10-30%","30-50%",">50%"]
        saved_i=ci.get("indirect_revenue_pct","")
        ind=st.radio("Range",i_opts,index=i_opts.index(saved_i) if saved_i in i_opts else 0,key="ci_ind",horizontal=True)

        st.markdown("**Discounts to channel partners** *(Select all that apply)*")
        disc_opts=["<15%","15-30%","30-50%",">60%","Other"]
        saved_disc=ci.get("discounts",[])
        disc_c=st.columns(len(disc_opts)); disc_sel=[]
        for i,o in enumerate(disc_opts):
            with disc_c[i]:
                if st.checkbox(o,value=o in saved_disc,key=f"ci_disc_{i}"): disc_sel.append(o)

        st.markdown("**Partner designations**")
        desig=st.text_input("Comma-separated, e.g. gold, silver, bronze",value=ci.get("partner_designations",""),key="ci_desig")

        st.markdown("---")
        _,cr=st.columns([3,1])
        with cr: ci_sub=st.form_submit_button("Next →  Step 1",use_container_width=True,type="primary")

    if ci_sub:
        st.session_state["client_info"]={"client_name":ci_name,"project_manager":ci_pm,"url":ci_url,"city":ci_city,"country":ci_country,"email":ci_email,"phone":ci_phone,"company_size":sz_sel,"verticals":v_sel,"other_verticals":other_v,"solution_delivery":d_sel,"avg_transaction_value":txn,"services_pct":svc,"services_comments":svc_c,"partner_count":pc,"indirect_revenue_pct":ind,"discounts":disc_sel,"partner_designations":desig}
        CLIENT_PATH.write_text(json.dumps(st.session_state["client_info"],indent=2))
        st.session_state["_ci_saved"]=True
        st.session_state["current_page"]="Step 1 — Scoring Criteria"
        st.rerun()

    if CLIENT_PATH.exists():
        st.markdown("---")
        with st.expander("📊 Download stored client data"):
            st.download_button("⬇️ Download client_info.json",CLIENT_PATH.read_text(),"client_info.json","application/json")

# ═════════════════════════════════════════════════════════════════════════
# 7. STEP 1 — SCORING CRITERIA
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 1 — Scoring Criteria":
    _brand()
    st.markdown("## Step 1 — Define Scoring Criteria")
    st.markdown("Configure **1–5** thresholds. Toggle metrics on/off with the checkbox.")

    if st.session_state.get("_p1_saved"):
        st.markdown('<div class="toast">✅ Criteria saved</div>',unsafe_allow_html=True)
        st.session_state["_p1_saved"]=False

    with st.form("p1_form"):
        for m in visible_metrics:
            mk=m["key"]; cr=st.session_state["criteria"][mk]; iq=m["type"]=="quantitative"
            ie=cr.get("enabled",True)
            tt='<span class="tag tag-q">Quantitative</span>' if iq else '<span class="tag tag-ql">Qualitative</span>'
            dt=f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
            xt='' if ie else '<span class="tag tag-del">EXCLUDED</span>'
            dc="" if ie else " mc-off"
            ud=f' ({m["unit"]})' if m.get("unit") else ""
            st.markdown(f'<div class="mc{dc}"><span class="mname">{m["id"]}. {m["name"]}</span>{tt}{dt}{xt}<div class="mexpl">{m["explanation"]}</div></div>',unsafe_allow_html=True)
            st.checkbox("Include in scoring",value=ie,key=f"p1_{mk}_en")
            if iq:
                cols=st.columns(5)
                for idx,s in enumerate(("1","2","3","4","5")):
                    with cols[idx]:
                        st.markdown(f'<div class="sb sb{s}">{s}</div>',unsafe_allow_html=True)
                        st.text_input(f"Min{ud}",value=cr["ranges"][s]["min"],key=f"p1_{mk}_s{s}_min",placeholder="No min" if s=="1" else "")
                        st.text_input(f"Max{ud}",value=cr["ranges"][s]["max"],key=f"p1_{mk}_s{s}_max",placeholder="No cap" if s=="5" else "")
            else:
                cols=st.columns(5)
                for idx,s in enumerate(("1","2","3","4","5")):
                    with cols[idx]:
                        st.markdown(f'<div class="sb sb{s}">{s}</div>',unsafe_allow_html=True)
                        st.text_area("desc",value=cr["descriptors"][s],key=f"p1_{mk}_s{s}_desc",height=100,label_visibility="collapsed")

        st.markdown("---")
        _,cm,cr=st.columns([2,1,1])
        with cm: p1s=st.form_submit_button("💾  Save Criteria",use_container_width=True,type="primary")
        with cr: p1n=st.form_submit_button("Next →  Step 2",use_container_width=True)

    if p1s or p1n:
        _save_criteria()
        st.session_state["_p1_saved"]=True
        if p1n: st.session_state["current_page"]="Step 2 — Score a Partner"
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════
# 8. STEP 2 — SCORE A PARTNER
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 2 — Score a Partner":
    _brand()
    st.markdown("## Step 2 — Score a Partner")

    if not SAVE_PATH.exists():
        st.warning("⚠️ Complete **Step 1** first.")
        st.stop()

    st.session_state["criteria"]=json.loads(SAVE_PATH.read_text())
    cr=st.session_state["criteria"]
    em=_enabled(); mx=len(em)*5

    if st.session_state.get("_p2_submitted"):
        st.markdown('<div class="toast">✅ Partner submitted & saved to CSV. Ready for next partner.</div>',unsafe_allow_html=True)
        st.session_state["_p2_submitted"]=False

    st.markdown(f"Enter performance data. Live scoring from Step 1 criteria. Total out of **{mx}** ({len(em)} metrics × 5).")

    # Partner details
    st.markdown('<div class="partner-hdr">Partner details</div>',unsafe_allow_html=True)
    tiers=_tiers(); t_opts=["Please choose..."]+tiers if tiers else ["Please choose...","(Set tiers in Client Intake)"]
    pc1,pc2,pc3=st.columns(3)
    with pc1: pn=st.text_input("Partner company name",key="p2_pn",placeholder="e.g. ABC reseller")
    with pc2: py=st.text_input("Year become partner",key="p2_py",placeholder="e.g. 2020")
    with pc3: pt=st.selectbox("Tier",t_opts,key="p2_pt")
    pc4,pc5=st.columns(2)
    with pc4: pcity=st.text_input("City",key="p2_city",placeholder="e.g. Paris")
    with pc5: pcountry=st.text_input("Country",key="p2_country",placeholder="e.g. France")

    st.markdown("---")

    # Filter enabled + category
    if chosen_cat=="All Metrics": ve=em
    else:
        cn=chosen_cat.split("  ",1)[-1]
        ck=next(c["keys"] for c in CATEGORIES if c["label"]==cn)
        ve=[m for m in em if m["key"] in ck]

    # Metric inputs with live scoring
    for m in ve:
        mk=m["key"]; mc=cr[mk]; iq=m["type"]=="quantitative"
        tt='<span class="tag tag-q">Quantitative</span>' if iq else '<span class="tag tag-ql">Qualitative</span>'
        dt=f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
        st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{tt}{dt}<div class="mexpl">{m["explanation"]}</div></div>',unsafe_allow_html=True)

        if iq:
            u=mc.get("unit","") or ""
            hints=[]
            for s in("1","2","3","4","5"):
                r=mc["ranges"][s]; lo,hi=r["min"],r["max"]
                if lo and hi: hints.append(f"<b>{s}</b>: {lo}–{hi}")
                elif lo and not hi: hints.append(f"<b>{s}</b>: ≥{lo}")
                elif not lo and hi: hints.append(f"<b>{s}</b>: ≤{hi}")
            if hints: st.markdown(f'<div class="hint-row">Ranges ({u}): {" &nbsp;·&nbsp; ".join(hints)}</div>',unsafe_allow_html=True)
            ic,sc_c=st.columns([4,1])
            with ic: pv=st.text_input(f"Value ({u})",key=f"p2_{mk}",placeholder=f"Enter number ({u})",label_visibility="collapsed")
            scr=score(mk,pv)
        else:
            opts=["— Select —"]+[f"({s}) {mc['descriptors'][s]}" for s in("1","2","3","4","5")]
            ic,sc_c=st.columns([4,1])
            with ic: pv=st.selectbox("Level",opts,key=f"p2_{mk}",label_visibility="collapsed")
            if pv and pv!="— Select —":
                raw_d=re.sub(r"^\(\d\)\s*","",pv); scr=score(mk,raw_d)
            else: scr=None
        with sc_c:
            if scr: st.markdown(f'<div class="live-score" style="background:{SC[scr]}">{scr}</div>',unsafe_allow_html=True)
            else: st.markdown('<div class="live-score" style="background:#ccc">—</div>',unsafe_allow_html=True)

    # Live summary
    st.markdown("---")
    full={}
    for m in em:
        mk=m["key"]; pv=st.session_state.get(f"p2_{mk}","")
        if not pv or pv=="— Select —": full[mk]=None
        elif m["type"]=="qualitative" and pv.startswith("("):
            full[mk]=score(mk,re.sub(r"^\(\d\)\s*","",pv))
        else: full[mk]=score(mk,pv)
    si={k:v for k,v in full.items() if v is not None}
    total=sum(si.values()); sn=len(si); mp=sn*5
    pct=(total/mp*100) if mp else 0; gl,gc=_grade(pct)
    pname=st.session_state.get("p2_pn","Partner") or "Partner"

    st.markdown(f"### Live Summary — {pname}")
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f'<div class="sum-card"><div class="sum-big">{total}</div><div class="sum-lbl">Total</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sum-card"><div class="sum-big">{sn}/{len(em)}</div><div class="sum-lbl">Scored</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="sum-card"><div class="sum-big">{pct:.1f}%</div><div class="sum-lbl">Percentage</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:{gc}">{gl}</div><div class="sum-lbl">Grade</div></div>',unsafe_allow_html=True)

    # Submit button
    st.markdown("---")
    _,_,submit_col=st.columns([2,2,1])
    with submit_col:
        if st.button("✅  Submit & Start New Partner",use_container_width=True,type="primary"):
            if not pname or pname=="Partner":
                st.error("Enter a partner name first.")
            else:
                # Build row and append to CSV
                row={"partner_name":pname,"partner_year":st.session_state.get("p2_py",""),
                     "partner_tier":st.session_state.get("p2_pt",""),"partner_city":st.session_state.get("p2_city",""),
                     "partner_country":st.session_state.get("p2_country",""),
                     "total_score":total,"max_possible":mp,"percentage":round(pct,1)}
                for m in em:
                    row[m["key"]]=full.get(m["key"],"")
                _append_partner_csv(row)
                # Clear partner fields for next entry
                for k in list(st.session_state.keys()):
                    if k.startswith("p2_"): del st.session_state[k]
                st.session_state["_p2_submitted"]=True
                st.rerun()

# ═════════════════════════════════════════════════════════════════════════
# 9. STEP 3 — PARTNER ASSESSMENT (heat map)
# ═════════════════════════════════════════════════════════════════════════
else:
    _brand()
    st.markdown("## Step 3 — Partner Assessment")

    partners=_load_all_partners()
    em=_enabled()

    if not partners:
        st.info("No partners scored yet. Complete **Step 2** to add partners.")
        st.stop()

    st.markdown(f"**{len(partners)}** partners scored across **{len(em)}** active metrics. Sorted by total score (highest first).")

    # Sort
    def sk(p):
        try: return -int(p.get("total_score",0))
        except: return 0
    ps=sorted(partners,key=sk)

    # Build HTML heat-map table
    hdr="<tr><th>Rank</th><th>Partner</th><th>Tier</th>"
    for m in em:
        short=m["name"][:20]
        hdr+=f'<th title="{m["name"]}">{short}</th>'
    hdr+="<th>Total</th><th>%</th></tr>"

    rows=""
    for ri,p in enumerate(ps,1):
        rows+=f"<tr><td><b>{ri}</b></td><td style='text-align:left;padding-left:10px'>{p.get('partner_name','')}</td><td>{p.get('partner_tier','')}</td>"
        for m in em:
            raw=p.get(m["key"],"")
            try: v=int(raw)
            except: v=None
            if v and 1<=v<=5:
                rows+=f'<td class="hm{v}">{v}</td>'
            else:
                rows+=f'<td style="color:#ccc">—</td>'
        try: tv=int(p.get("total_score",0))
        except: tv=0
        try: pv=float(p.get("percentage",0))
        except: pv=0
        rows+=f'<td class="hm-total">{tv}</td><td class="hm-total">{pv:.1f}%</td></tr>'

    st.markdown(f'<div style="overflow-x:auto"><table class="hm-tbl"><thead>{hdr}</thead><tbody>{rows}</tbody></table></div>',unsafe_allow_html=True)

    # Download as XLSX
    st.markdown("---")
    xlsx_bytes = _generate_assessment_xlsx(ps, em)
    if xlsx_bytes:
        st.download_button("⬇️  Download as Excel Spreadsheet", xlsx_bytes,
            "Partner_Assessment.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary")
    else:
        st.warning("Install openpyxl for Excel export: `pip install openpyxl`")

    # Also offer CSV
    if ALL_PARTNERS_CSV.exists():
        st.download_button("⬇️  Download raw CSV", ALL_PARTNERS_CSV.read_text(),
            "all_partners.csv", "text/csv")
