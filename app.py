"""
ChannelPRO — Partner Revenue Optimizer (Multi-Tenant v4)
========================================================
Login → Client Intake → Step 1–4
Single instance, per-client data isolation, admin overview.
"""
import csv, hashlib, io, json, os, pathlib, re, secrets
import streamlit as st
import pandas as pd

# ═════════════════════════════════════════════════════════════════════════
# DATA & AUTH PATHS
# ═════════════════════════════════════════════════════════════════════════
BASE_DIR = pathlib.Path(os.environ.get("RENDER_DISK_PATH", "."))
BASE_DIR.mkdir(parents=True, exist_ok=True)
USERS_FILE = BASE_DIR / "users.json"
TENANTS_DIR = BASE_DIR / "tenants"
TENANTS_DIR.mkdir(parents=True, exist_ok=True)

YORK_LOGO_B64 = "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"


# ═════════════════════════════════════════════════════════════════════════
# COUNTRIES LIST
# ═════════════════════════════════════════════════════════════════════════
COUNTRIES = ["","Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo","Costa Rica","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Ivory Coast","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]

# ═════════════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═════════════════════════════════════════════════════════════════════════
def _hash_pw(pw):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000)
    return f"{salt}:{h.hex()}"

def _verify_pw(pw, stored):
    try:
        salt, h = stored.split(":")
        return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex() == h
    except Exception: return False

def _load_users():
    if USERS_FILE.exists():
        try: return json.loads(USERS_FILE.read_text())
        except Exception: pass
    default = {"admin": {"password_hash": _hash_pw("admin"), "display_name": "Administrator", "role": "admin", "tenant": None}}
    _save_users(default); return default

def _save_users(users): USERS_FILE.write_text(json.dumps(users, indent=2))

def _tenant_dir(tid):
    d = TENANTS_DIR / tid; d.mkdir(parents=True, exist_ok=True); return d

def _all_tenants():
    if not TENANTS_DIR.exists(): return []
    return sorted([d.name for d in TENANTS_DIR.iterdir() if d.is_dir()])

def _current_data_dir():
    tid = st.session_state.get("active_tenant")
    return _tenant_dir(tid) if tid else BASE_DIR

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
    {"label":"Revenue & Growth","icon":"💰","keys":["annual_revenues","yoy_revenue_growth","net_new_logo_revenues","pct_revenues_saas","net_revenue_expansion","total_revenues"]},
    {"label":"Sales Performance","icon":"📈","keys":["avg_deal_size_net_new","avg_deal_size_renewals","avg_time_to_close","registered_deals","win_loss_ratio","partner_generated_opps_pct","frequency_of_business"]},
    {"label":"Retention & Satisfaction","icon":"🤝","keys":["renewal_rate","customer_satisfaction","communication_with_vendor"]},
    {"label":"Enablement & Support","icon":"🎓","keys":["mdf_utilization_rate","quality_of_sales_org","vendor_certifications","sales_support_calls","tech_support_calls"]},
    {"label":"Strategic Fit","icon":"🧭","keys":["dedication_vs_competitive","dedication_vs_other_vendors","geographical_coverage","vertical_coverage"]},
    {"label":"Risk & Governance","icon":"🛡️","keys":["quality_of_management","known_litigation","export_control_ip","financial_strength"]},
]
METRICS_BY_KEY = {m["key"]: m for m in SCORECARD_METRICS}
SC = {1:"#dc4040",2:"#e8820c",3:"#d4a917",4:"#49a34f",5:"#1b6e23"}




# ═════════════════════════════════════════════════════════════════════════
# TENANT-AWARE DATA HELPERS
# ═════════════════════════════════════════════════════════════════════════
def _save_path(): return _current_data_dir() / "scoring_criteria.json"
def _client_path(): return _current_data_dir() / "client_info.json"
def _csv_path(): return _current_data_dir() / "all_partners.csv"
def _class_path(): return _current_data_dir() / "classification_config.json"
def _raw_path(): return _current_data_dir() / "all_partners_raw.json"
def _tenant_config_path(tid=None):
    if tid:
        return _tenant_dir(tid) / "tenant_config.json"
    return _current_data_dir() / "tenant_config.json"

def _load_tenant_config(tid=None):
    tp = _tenant_config_path(tid)
    if tp.exists():
        try: return json.loads(tp.read_text())
        except: pass
    return {}

def _save_tenant_config(cfg, tid=None):
    _tenant_config_path(tid).write_text(json.dumps(cfg, indent=2))

def _max_partners():
    """Return max partner limit for current tenant (0 = unlimited)."""
    return _load_tenant_config().get("max_partners", 0)

def _partner_count():
    """Return current number of partners."""
    return len(_load_partners())

def _sf(val):
    if val is None: return None
    c = re.sub(r"[,$%\s]","",str(val).strip())
    if c == "": return None
    try: return float(c)
    except ValueError: return None

def _init_criteria():
    if "criteria" in st.session_state: return
    sp = _save_path()
    if sp.exists():
        try: st.session_state["criteria"]=json.loads(sp.read_text()); return
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
    _save_path().write_text(json.dumps(cr,indent=2))
    # Re-score ALL existing partners with updated criteria
    _rescore_all()

def calc_score(mk, val, criteria=None):
    cr = (criteria or st.session_state.get("criteria",{})).get(mk)
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

def _enabled(criteria=None):
    cr = criteria or st.session_state.get("criteria",{})
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
    # Always ensure client_info is loaded with logo from tenant file
    ci = st.session_state.get("client_info")
    if not ci or not ci.get("logo_url"):
        cp = _client_path()
        if cp.exists():
            try:
                disk_ci = json.loads(cp.read_text())
                if disk_ci.get("logo_url"):
                    if ci:
                        ci["logo_url"] = disk_ci["logo_url"]
                    else:
                        st.session_state["client_info"] = disk_ci
                        ci = disk_ci
            except: pass
    logo_url = (ci or {}).get("logo_url", "")
    right_logo = f'<img src="{logo_url}" style="max-height:50px;border-radius:6px;" onerror="this.style.display=\'none\'">' if logo_url else ''
    st.markdown(f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;"><img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;border-radius:6px;"><div><div style="font-size:1.6rem;font-weight:800;color:#1e2a3a;">ChannelPRO</div><div style="font-size:.92rem;color:#4a6a8f;font-weight:600;margin-top:-4px;">Partner Revenue Optimizer</div></div><div style="margin-left:auto;">{right_logo}</div></div>',unsafe_allow_html=True)

# ─── Raw-value storage for re-scoring ────────────────────────────────
def _save_raw(partner_raw):
    rp = _raw_path()
    all_raw = json.loads(rp.read_text()) if rp.exists() else []
    found = False
    for i, r in enumerate(all_raw):
        if r.get("partner_name") == partner_raw.get("partner_name"):
            all_raw[i] = partner_raw; found = True; break
    if not found: all_raw.append(partner_raw)
    rp.write_text(json.dumps(all_raw, indent=2))

def _load_raw():
    rp = _raw_path()
    if rp.exists():
        try: return json.loads(rp.read_text())
        except: pass
    return []

def _rescore_all():
    """Re-score all partners using current criteria and rewrite CSV."""
    raw_partners = _load_raw()
    if not raw_partners: return
    cr = st.session_state.get("criteria")
    if not cr: return
    em = _enabled(cr)
    em_keys = {m["key"] for m in em}
    cp = _csv_path()
    fnames = ["partner_name","partner_year","partner_tier","partner_discount","partner_city","partner_country","pam_name","pam_email"]
    fnames += [m["key"] for m in em]
    fnames += ["total_score","max_possible","percentage"]
    with open(cp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
        w.writeheader()
        for rp in raw_partners:
            row = {k: rp.get(k,"") for k in ["partner_name","partner_year","partner_tier","partner_discount","partner_city","partner_country","pam_name","pam_email"]}
            si = {}
            for m in em:
                mk = m["key"]
                raw_val = rp.get(f"raw_{mk}")
                scr = calc_score(mk, raw_val, cr) if raw_val else None
                row[mk] = scr if scr else ""
                if scr: si[mk] = scr
            total = sum(si.values()); sn = len(si); mp = sn * 5
            row["total_score"] = total; row["max_possible"] = mp
            row["percentage"] = round(total / mp * 100, 1) if mp else 0
            w.writerow(row)

def _append_partner(row_dict, raw_dict):
    em = _enabled()
    fnames = ["partner_name","partner_year","partner_tier","partner_discount","partner_city","partner_country","pam_name","pam_email"]
    fnames += [m["key"] for m in em]
    fnames += ["total_score","max_possible","percentage"]
    cp = _csv_path(); exists = cp.exists()
    with open(cp, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
        if not exists: w.writeheader()
        w.writerow(row_dict)
    _save_raw(raw_dict)

def _load_partners(path=None):
    cp = path or _csv_path()
    if not cp.exists(): return []
    with open(cp, newline="") as f:
        return list(csv.DictReader(f))

def _delete_partner(partner_name):
    # Remove from raw
    rp = _raw_path()
    if rp.exists():
        raw = [r for r in json.loads(rp.read_text()) if r.get("partner_name") != partner_name]
        rp.write_text(json.dumps(raw, indent=2))
    # Remove from CSV
    cp = _csv_path()
    if cp.exists():
        partners = [p for p in _load_partners() if p.get("partner_name") != partner_name]
        if partners:
            with open(cp, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(partners[0].keys()))
                w.writeheader()
                for p in partners: w.writerow(p)
        else:
            cp.unlink()

def _partner_exists(name):
    return any(p.get("partner_name","").strip().lower() == name.strip().lower() for p in _load_partners())

def _upsert_partner(row_dict, raw_dict):
    """Create or update a partner. If name exists, replace; else append."""
    pn = row_dict.get("partner_name","").strip()
    if not pn: return
    # Remove existing if present (from both CSV and raw)
    existing = _load_partners()
    if any(p.get("partner_name","").strip().lower() == pn.lower() for p in existing):
        _delete_partner(pn)
    _append_partner(row_dict, raw_dict)

def _synthetic_raw_for_score(mk, score, cr=None):
    """Given a metric key and desired score (1-5), return a raw value that calc_score would map to that score."""
    if score is None or score == 0: return None
    criteria = cr or st.session_state.get("criteria",{})
    mc = criteria.get(mk)
    if not mc: return str(score)
    if mc["type"] == "qualitative":
        # Return the descriptor text for that score level
        return mc.get("descriptors",{}).get(str(score),"")
    else:
        # Quantitative — pick a value in the middle of the range
        r = mc.get("ranges",{}).get(str(score),{})
        lo, hi = _sf(r.get("min")), _sf(r.get("max"))
        if lo is not None and hi is not None:
            return str((lo + hi) / 2)
        elif lo is not None:
            return str(lo + 1)  # just above minimum
        elif hi is not None:
            return str(hi)
        return str(score)


# ═════════════════════════════════════════════════════════════════════════
# AI AGENT HELPERS — Ask ChannelPRO
# ═════════════════════════════════════════════════════════════════════════
def _build_ai_system_prompt():
    """Build a system prompt containing all partner data and criteria definitions."""
    cr = st.session_state.get("criteria", {})
    em = _enabled(cr)
    partners = _load_partners()
    raw_all = _load_raw()
    raw_by_name = {r.get("partner_name",""): r for r in raw_all}

    # Build criteria reference
    criteria_lines = []
    for m in em:
        mc = cr.get(m["key"], {})
        if m["type"] == "quantitative":
            ranges = []
            for s in ("1","2","3","4","5"):
                r = mc.get("ranges",{}).get(s,{})
                lo, hi = r.get("min",""), r.get("max","")
                if lo and hi: ranges.append(f"  {s}: {lo}–{hi}")
                elif lo: ranges.append(f"  {s}: ≥{lo}")
                elif hi: ranges.append(f"  {s}: ≤{hi}")
            criteria_lines.append(f"- {m['name']} (key: {m['key']}, unit: {m.get('unit','')}, {m['direction']}, quantitative)\n" + "\n".join(ranges))
        else:
            descs = [f"  {s}: {mc.get('descriptors',{}).get(s,'')}" for s in ("1","2","3","4","5")]
            criteria_lines.append(f"- {m['name']} (key: {m['key']}, {m['direction']}, qualitative)\n" + "\n".join(descs))

    # Build partner data table
    partner_lines = []
    for p in partners:
        raw = raw_by_name.get(p.get("partner_name",""), {})
        metrics_str = []
        for m in em:
            mk = m["key"]
            try: score = int(p.get(mk,"") or 0)
            except: score = 0
            raw_val = raw.get(f"raw_{mk}", "")
            if score and raw_val:
                metrics_str.append(f"{m['name']}={score}/5 (raw:{raw_val})")
            elif score:
                metrics_str.append(f"{m['name']}={score}/5")
            else:
                metrics_str.append(f"{m['name']}=unscored")
        try: pct = float(p.get("percentage",0) or 0)
        except: pct = 0
        try: total = int(p.get("total_score",0) or 0)
        except: total = 0
        partner_lines.append(
            f"Partner: {p.get('partner_name','')}\n"
            f"  Tier: {p.get('partner_tier','N/A')} | Country: {p.get('partner_country','N/A')} | "
            f"City: {p.get('partner_city','N/A')} | PAM: {p.get('pam_name','N/A')} | "
            f"Discount: {p.get('partner_discount','N/A')}\n"
            f"  Total: {total} | Percentage: {pct:.1f}%\n"
            f"  Scores: {' | '.join(metrics_str)}"
        )

    system = f"""You are ChannelPRO AI Assistant, an expert in partner channel management and analysis.
You analyze partner scorecard data and provide actionable insights.

SCORING SYSTEM: Each metric is scored 1-5 (5=best). Higher percentage = better overall performance.
Grade scale: A (≥90%), B+ (≥80%), B (≥70%), C+ (≥60%), C (≥50%), D (<50%).

SCORING CRITERIA ({len(em)} active metrics):
{chr(10).join(criteria_lines)}

PARTNER DATA ({len(partners)} partners):
{chr(10).join(partner_lines) if partner_lines else "No partners scored yet."}

INSTRUCTIONS:
- Answer questions about partner performance, comparisons, filtering, and trends.
- When listing partners, include their key metrics and scores.
- You can suggest or make score updates when asked.
- Be specific with numbers and partner names.

Always respond with valid JSON (no markdown fences, no extra text) in this exact format:
{{
  "answer": "Your detailed analysis in plain text. Use \\n for line breaks.",
  "table": [
    {{"Partner": "Name", "Tier": "Gold", "Country": "US", "PAM": "Jane", "Total": 85, "Pct": "72.3%", "Key Metric": "value"}}
  ],
  "chart": {{
    "type": "bar or pie or hbar",
    "title": "Chart title",
    "x_label": "X axis label",
    "y_label": "Y axis label",
    "data": [{{"label": "Name", "value": 42.5}}, {{"label": "Name2", "value": 38.1}}]
  }},
  "updates": [
    {{"partner": "Partner Name", "metric_key": "metric_key_here", "new_score": 3, "reason": "Explanation"}}
  ]
}}

RULES for the JSON response:
- "answer" is ALWAYS required.
- "table" should be included when listing/filtering partners. Use null if not relevant. Include only the most relevant columns.
- "chart" should be included when a visualization would help (comparisons, distributions, rankings). Use null if not needed. Keep data to ≤15 items for readability.
- "updates" should ONLY be included when the user explicitly asks to change/update scores. Use null otherwise. Only update scores to values 1-5.
- For "table", dynamically choose columns that are relevant to the query.
- For "chart", choose the best chart type: "bar" for comparisons, "pie" for distributions, "hbar" for ranked lists.
"""
    return system

def _call_ai(messages, api_key):
    """Call Anthropic API with conversation history."""
    import requests as req
    system = _build_ai_system_prompt()
    try:
        resp = req.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 4096, "system": system, "messages": messages},
            timeout=60)
        if resp.status_code != 200:
            return {"answer": f"API error ({resp.status_code}): {resp.text}", "table": None, "chart": None, "updates": None}
        data = resp.json()
        text = "".join(b.get("text","") for b in data.get("content",[]) if b.get("type")=="text")
        # Parse JSON from response
        text = text.strip()
        # Strip markdown fences if present
        if text.startswith("```"): text = re.sub(r"^```(?:json)?\s*","",text); text = re.sub(r"\s*```$","",text)
        return json.loads(text)
    except json.JSONDecodeError:
        return {"answer": text if 'text' in dir() else "Could not parse AI response.", "table": None, "chart": None, "updates": None}
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "table": None, "chart": None, "updates": None}

def _render_ai_chart(chart_spec):
    """Render a chart from AI-generated spec using Altair."""
    import altair as alt
    if not chart_spec or not chart_spec.get("data"): return
    ctype = chart_spec.get("type", "bar")
    title = chart_spec.get("title", "")
    data = chart_spec["data"]
    df = pd.DataFrame(data)
    if "label" not in df.columns or "value" not in df.columns: return

    if ctype == "pie":
        chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("value:Q"),
            color=alt.Color("label:N", legend=alt.Legend(title="")),
            tooltip=["label:N", alt.Tooltip("value:Q", format=".1f")]
        ).properties(title=title, height=350)
    elif ctype == "hbar":
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y("label:N", sort="-x", title=chart_spec.get("y_label","")),
            x=alt.X("value:Q", title=chart_spec.get("x_label","")),
            color=alt.Color("value:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["label:N", alt.Tooltip("value:Q", format=".1f")]
        ).properties(title=title, height=max(len(data)*28, 200))
    else:  # bar
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("label:N", sort="-y", axis=alt.Axis(labelAngle=-45, labelLimit=120), title=chart_spec.get("x_label","")),
            y=alt.Y("value:Q", title=chart_spec.get("y_label","")),
            color=alt.Color("value:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["label:N", alt.Tooltip("value:Q", format=".1f")]
        ).properties(title=title, height=350)
    st.altair_chart(chart, use_container_width=True)

def _apply_ai_updates(updates, cr):
    """Apply score updates from AI response."""
    em = _enabled(cr)
    em_keys = {m["key"] for m in em}
    partners = _load_partners()
    raw_all = _load_raw()
    applied = 0
    for upd in updates:
        pn = upd.get("partner","")
        mk = upd.get("metric_key","")
        new_score = upd.get("new_score")
        if not pn or not mk or mk not in em_keys: continue
        if not isinstance(new_score, int) or new_score < 1 or new_score > 5: continue
        # Find partner
        csv_p = next((p for p in partners if p.get("partner_name","").strip().lower() == pn.strip().lower()), None)
        raw_p = next((r for r in raw_all if r.get("partner_name","").strip().lower() == pn.strip().lower()), None)
        if not csv_p: continue
        # Update score
        csv_p[mk] = new_score
        if raw_p:
            raw_p[f"raw_{mk}"] = _synthetic_raw_for_score(mk, new_score, cr)
        # Recalculate totals
        si = {}
        for m in em:
            try: v = int(csv_p.get(m["key"],"") or 0)
            except: v = 0
            if v and 1 <= v <= 5: si[m["key"]] = v
        total = sum(si.values()); sn = len(si); mp = sn * 5
        csv_p["total_score"] = total; csv_p["max_possible"] = mp
        csv_p["percentage"] = round(total / mp * 100, 1) if mp else 0
        applied += 1
    # Rewrite files
    if applied > 0:
        cp = _csv_path()
        if partners:
            fnames = list(partners[0].keys())
            with open(cp, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
                w.writeheader()
                for p in partners: w.writerow(p)
        rp = _raw_path()
        rp.write_text(json.dumps(raw_all, indent=2))
    return applied


def _gen_xlsx(partners, enabled_metrics):
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    except ImportError: return None
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Partner Assessment"
    fills={1:PatternFill(start_color="FA7A7A",end_color="FA7A7A",fill_type="solid"),2:PatternFill(start_color="FFFFCC",end_color="FFFFCC",fill_type="solid"),3:PatternFill(start_color="FFFFCC",end_color="FFFFCC",fill_type="solid"),4:PatternFill(start_color="C6EFCE",end_color="C6EFCE",fill_type="solid"),5:PatternFill(start_color="C6EFCE",end_color="C6EFCE",fill_type="solid")}
    hf=PatternFill(start_color="1E2A3A",end_color="1E2A3A",fill_type="solid"); hfont=Font(color="FFFFFF",bold=True,size=10)
    bdr=Border(left=Side(style="thin",color="CCCCCC"),right=Side(style="thin",color="CCCCCC"),top=Side(style="thin",color="CCCCCC"),bottom=Side(style="thin",color="CCCCCC"))
    headers=["Rank","Partner Name","Tier","PAM","City","Country"]+[m["name"] for m in enabled_metrics]+["Total","%"]
    for c,h in enumerate(headers,1):
        cell=ws.cell(1,c,h); cell.fill=hf; cell.font=hfont; cell.alignment=Alignment(horizontal="center",wrap_text=True); cell.border=bdr
        ws.column_dimensions[cell.column_letter].width=14 if c>6 else 18
    ps=sorted(partners,key=lambda p:-int(p.get("total_score",0) or 0))
    for ri,p in enumerate(ps,2):
        ws.cell(ri,1,ri-1).border=bdr; ws.cell(ri,1).alignment=Alignment(horizontal="center")
        ws.cell(ri,2,p.get("partner_name","")).border=bdr
        ws.cell(ri,3,p.get("partner_tier","")).border=bdr
        ws.cell(ri,4,p.get("pam_name","")).border=bdr
        ws.cell(ri,5,p.get("partner_city","")).border=bdr
        ws.cell(ri,6,p.get("partner_country","")).border=bdr
        for ci,m in enumerate(enabled_metrics,7):
            try: v=int(p.get(m["key"],"") or 0)
            except: v=None
            cell=ws.cell(ri,ci); cell.border=bdr; cell.alignment=Alignment(horizontal="center")
            if v and 1<=v<=5: cell.value=v; cell.fill=fills[v]; cell.font=Font(bold=True)
        tc=len(enabled_metrics)+7
        try: tv=int(p.get("total_score",0) or 0)
        except: tv=0
        ws.cell(ri,tc,tv).border=bdr; ws.cell(ri,tc).font=Font(bold=True); ws.cell(ri,tc).alignment=Alignment(horizontal="center")
        try: pv=float(p.get("percentage",0) or 0)
        except: pv=0
        pc=ws.cell(ri,tc+1); pc.value=pv/100; pc.number_format="0.0%"; pc.border=bdr; pc.alignment=Alignment(horizontal="center"); pc.font=Font(bold=True)
    buf=io.BytesIO(); wb.save(buf); return buf.getvalue()

# ═════════════════════════════════════════════════════════════════════════
# CLASSIFICATION ENGINE — 3 quadrants + Long Tail
# ═════════════════════════════════════════════════════════════════════════
METRIC_ALIASES = {"total company revenues":"total_revenues","annual vendor revenues":"annual_revenues","annual revenues":"annual_revenues","y-y growth rate":"yoy_revenue_growth","y-y revenue growth":"yoy_revenue_growth","year-on-year revenue growth":"yoy_revenue_growth","net new logo growth":"net_new_logo_revenues","net-new logo revenues":"net_new_logo_revenues","# of known competitors":None,"your product ranking":None,"average deal size":"avg_deal_size_net_new","average time to close":"avg_time_to_close"}
for _m in SCORECARD_METRICS:
    METRIC_ALIASES[_m["key"]]=_m["key"]; METRIC_ALIASES[_m["name"].lower()]=_m["key"]

DEFAULT_Q_CONFIG = {1:[("total_revenues","high"),("annual_revenues","low"),("yoy_revenue_growth","low")],2:[("annual_revenues","high"),("yoy_revenue_growth","high"),("net_new_logo_revenues","high")],3:[("annual_revenues","high"),("yoy_revenue_growth","low"),("net_new_logo_revenues","mid")]}

def _level_match(sv, level):
    try: v=int(sv)
    except: return False
    if v==0: return False
    if level is None or level=="any": return v>0
    if level=="high": return v>=4
    if level=="mid": return v==3
    if level=="low": return v<=2
    return False

def classify_partners(partners, qconfig, em_keys):
    results={}
    for p in partners:
        name=p.get("partner_name","Unknown")
        try: total=int(p.get("total_score",0) or 0)
        except: total=0
        if total==0: continue
        assigned=None
        for qn in sorted(qconfig.keys()):
            crit=qconfig[qn]; match=True
            for(mk,lvl) in crit:
                if mk is None or mk not in em_keys: continue
                if not _level_match(p.get(mk),lvl): match=False; break
            if match and crit: assigned=qn; break
        results[name]=assigned if assigned is not None else 4  # 4 = Long Tail
    return results

def _load_q_config():
    cp=_class_path()
    if cp.exists():
        try:
            raw=json.loads(cp.read_text())
            return {int(k):[(tuple(i) if isinstance(i,list) else i) for i in v] for k,v in raw.items()}
        except: pass
    return DEFAULT_Q_CONFIG.copy()

def _save_q_config(config): _class_path().write_text(json.dumps({str(k):v for k,v in config.items()},indent=2))

Q_LABELS={1:("Strategic / Underperforming","#2563eb"),2:("Top Performers","#1b6e23"),3:("Growth Potential","#d4a917"),4:("Long Tail","#dc4040")}
Q_DESCS={1:"High total revenue but low vendor-specific performance",2:"Strong across revenue, growth, and new logos",3:"Good revenue but stagnant growth",4:"Does not meet criteria for quadrants 1–3"}

# ═════════════════════════════════════════════════════════════════════════
# BREAK-EVEN DEFAULTS (from "Nominal break-even" sheet)
# ═════════════════════════════════════════════════════════════════════════
BE_SECTIONS = [
    {"section":"Personnel and Overhead","items":[
        "Partner managers - salaries and commissions","Social charges","Office space",
        "Phone, laptop, software","Admin and order processing","Overhead allocation"]},
    {"section":"Infrastructure and Technology","items":[
        "PRM and other software used for the channel","Integration with partner systems",
        "Security for data sharing and privacy regulations"]},
    {"section":"Marketing and Promotion","items":[
        "Co-marketing and MDF","SEO and other campaigns","Marketing collateral",
        "Website maintenance","Incentives - spiffs, rebates, sales contests","Events and conferences"]},
    {"section":"Technical and Sales Support","items":[
        "Technical support salaries","Pre-sales support salaries","Social charges",
        "Office space","Phone, laptop, software","Overhead allocation"]},
    {"section":"Training and Certification","items":[
        "Product training","Sales training","Certification programs"]},
    {"section":"Legal and Compliance","items":[
        "Contracts","Compliance","Conflict resolution - contract disputes and mediation"]},
    {"section":"Travel and Meetings","items":[
        "Face-to-face meetings","Joint sales calls"]},
    {"section":"Performance Metrics and Reporting","items":[
        "Partner performance tools salary","Reporting"]},
    {"section":"Scaling and Expansion","items":[
        "Partner recruitment manager","Social charges","Office space","Overhead allocation",
        "Phone, laptop, software","Partner recruitment marketing","Travel and meetings","Onboarding costs"]},
]
BE_SECTION_ICONS = {"Personnel and Overhead":"👥","Infrastructure and Technology":"🖥️",
    "Marketing and Promotion":"📣","Technical and Sales Support":"🛠️",
    "Training and Certification":"🎓","Legal and Compliance":"⚖️",
    "Travel and Meetings":"✈️","Performance Metrics and Reporting":"📊",
    "Scaling and Expansion":"🚀"}

def _be_path(): return _current_data_dir() / "break_even_configs.json"
def _sd_path(): return _current_data_dir() / "support_data.csv"

def _load_be():
    p = _be_path()
    if p.exists():
        try: return json.loads(p.read_text())
        except: pass
    # Build default config with all zeros
    cfg = {"sections": {}, "num_partners": 0, "support_calls": 0, "avg_min_per_call": 20}
    for sec in BE_SECTIONS:
        cfg["sections"][sec["section"]] = {item: 0 for item in sec["items"]}
    return cfg

def _save_be(cfg):
    _be_path().write_text(json.dumps(cfg, indent=2))


# ═════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & CSS
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
[data-testid="stAppViewContainer"] input[type="text"],[data-testid="stAppViewContainer"] textarea{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important}
[data-testid="stAppViewContainer"] input[type="text"]:focus,[data-testid="stAppViewContainer"] textarea:focus{background:#fff!important;border-color:#2563eb!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div:focus-within{background:#fff!important;border-color:#2563eb!important}
.hm-tbl{width:100%;border-collapse:collapse;font-size:.82rem;background:#fff;margin:1rem 0}
.hm-tbl th{background:#1e2a3a;color:#fff;padding:8px 6px;text-align:center;font-weight:700;font-size:.72rem;text-transform:uppercase;white-space:nowrap;border:1px solid #2a3d57}
.hm-tbl th.hm-diag{white-space:nowrap;vertical-align:bottom;height:140px;padding:0 4px 8px;width:36px;min-width:36px}
.hm-tbl th.hm-diag > div{transform:rotate(-55deg);transform-origin:bottom left;width:1.8em;margin-left:12px}
.hm-tbl td{padding:6px;text-align:center;border:1px solid #e2e6ed;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:.82rem}
.scroll-tbl{overflow-x:auto;overflow-y:auto;max-height:80vh;border:1px solid #e2e6ed;border-radius:10px}
.hm1{background:#FA7A7A;color:#fff}.hm2{background:#FFFFCC;color:#333}.hm3{background:#FFFFCC;color:#333}
.hm4{background:#C6EFCE;color:#1b6e23}.hm5{background:#C6EFCE;color:#1b6e23}
.hm-total{background:#1e2a3a;color:#fff;font-weight:800}
.q-card{border-radius:12px;padding:18px 22px;margin-bottom:14px;border:2px solid #e2e6ed}
.q-badge{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:10px;font-size:1.1rem;font-weight:800;color:#fff;font-family:'JetBrains Mono',monospace;margin-right:10px}
.q-partner{display:inline-block;padding:4px 14px;border-radius:8px;margin:3px 4px;font-size:.88rem;font-weight:600;background:#f0f2f7;color:#1e2a3a}
.q-criteria{font-size:.82rem;color:#5a6a7e;margin-top:6px;line-height:1.6}
.score-pill{display:inline-block;padding:3px 14px;border-radius:20px;font-weight:800;font-size:.82rem;color:#fff;min-width:28px;text-align:center;font-family:'JetBrains Mono',monospace}
.login-box{max-width:420px;margin:80px auto;background:#fff;border-radius:16px;padding:40px;box-shadow:0 4px 24px rgba(0,0,0,.08)}
.tenant-badge{display:inline-block;padding:4px 12px;border-radius:8px;font-size:.82rem;font-weight:700;background:#2563eb;color:#fff;margin-bottom:8px}
.plist-item{display:flex;align-items:center;justify-content:space-between;padding:8px 14px;border:1px solid #e2e6ed;border-radius:8px;margin:4px 0;background:#fff;font-size:.88rem}
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:#dc4040!important;border-color:#dc4040!important;color:#fff!important;font-weight:800!important}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ═════════════════════════════════════════════════════════════════════════
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

if st.session_state["auth_user"] is None:
    st.markdown(f"""<div class="login-box">
        <div style="text-align:center;margin-bottom:24px;">
            <img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;border-radius:6px;margin-bottom:12px;"><br>
            <span style="font-size:1.4rem;font-weight:800;color:#1e2a3a;">ChannelPRO</span><br>
            <span style="font-size:.88rem;color:#4a6a8f;">Partner Revenue Optimizer</span>
        </div></div>""", unsafe_allow_html=True)
    users = _load_users()
    with st.form("login_form"):
        uname = st.text_input("Username", placeholder="Enter your username")
        pw = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
    if submitted:
        if uname in users and _verify_pw(pw, users[uname]["password_hash"]):
            st.session_state["auth_user"] = uname
            u = users[uname]
            st.session_state["auth_role"] = u["role"]
            st.session_state["auth_display"] = u["display_name"]
            st.session_state["auth_tenant"] = u.get("tenant")
            if u["role"] == "admin":
                tenants = _all_tenants()
                st.session_state["active_tenant"] = tenants[0] if tenants else None
            else:
                st.session_state["active_tenant"] = u["tenant"]
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.caption("Default admin login: **admin** / **admin** — change this after first login!")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════
# LOGGED IN — INIT
# ═════════════════════════════════════════════════════════════════════════
is_admin = st.session_state.get("auth_role") == "admin"
active_tenant = st.session_state.get("active_tenant")
if active_tenant:
    _tenant_dir(active_tenant)
    _init_criteria()
    if "client_info" not in st.session_state:
        cp = _client_path()
        if cp.exists():
            try: st.session_state["client_info"]=json.loads(cp.read_text())
            except: st.session_state["client_info"]={}
        else: st.session_state["client_info"]={}
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Client Intake"


# ═════════════════════════════════════════════════════════════════════════
# SIDEBAR (with clickable partner list + PAM filter)
# ═════════════════════════════════════════════════════════════════════════
CLIENT_PAGES = ["Client Intake","Step 1 — Scoring Criteria","Step 2 — Score a Partner","Step 3 — Partner Assessment","Step 4 — Partner Classification","Import Data","Partner List","Ask ChannelPRO","Break-even — Program Costs","Break-even — Detailed Analysis"]
ADMIN_PAGES = CLIENT_PAGES + ["Admin — Manage Users","Admin — All Clients"]

with st.sidebar:
    _logo()
    st.markdown("**ChannelPRO** — Partner Revenue Optimizer")
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.get('auth_display','User')}**")
    if is_admin:
        st.markdown('<span class="tenant-badge">ADMIN</span>', unsafe_allow_html=True)
    elif active_tenant:
        st.markdown(f'<span class="tenant-badge">{active_tenant}</span>', unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True, type="primary"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.markdown("---")

    if is_admin:
        tenants = _all_tenants()
        if tenants:
            cur_idx = tenants.index(active_tenant) if active_tenant in tenants else 0
            selected = st.selectbox("🏢 Active Client", tenants, index=cur_idx, key="tenant_sel")
            if selected != active_tenant:
                st.session_state["active_tenant"] = selected
                for k in ["criteria","client_info","_p1_saved","_ci_saved","_p2_submitted","_q_saved","q_config"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            st.info("No clients yet. Create one in Manage Users.")
        st.markdown("---")

    pages = ADMIN_PAGES if is_admin else CLIENT_PAGES
    page = st.radio("Navigate", pages,
        index=pages.index(st.session_state["current_page"]) if st.session_state["current_page"] in pages else 0,
        key="nav_radio", label_visibility="collapsed")
    st.session_state["current_page"] = page
    st.markdown("---")

    chosen_cat = "All Metrics"
    if page not in ("Client Intake","Step 3 — Partner Assessment","Step 4 — Partner Classification","Import Data","Partner List","Ask ChannelPRO","Break-even — Program Costs","Break-even — Detailed Analysis","Admin — Manage Users","Admin — All Clients"):
        cat_labels=["All Metrics"]+[f"{c['icon']}  {c['label']}" for c in CATEGORIES]
        chosen_cat=st.radio("Category",cat_labels,index=0,label_visibility="collapsed")
    st.markdown("---")

    if active_tenant:
        if _save_path().exists(): st.success("✅ Criteria saved")
        else: st.info("ℹ️ Complete Step 1 first")
        en=_enabled()
        st.metric("Active Metrics",len(en))
        partners=_load_partners()
        # Clickable partner count → expandable list with delete
        mp_limit = _max_partners()
        limit_lbl = f" / {mp_limit}" if mp_limit else ""
        with st.expander(f"📋 Partners Scored: **{len(partners)}{limit_lbl}**"):
            if partners:
                # PAM filter
                pam_names = sorted(set(p.get("pam_name","").strip() for p in partners if p.get("pam_name","").strip()))
                if pam_names:
                    pam_filter = st.selectbox("Filter by PAM", ["All"] + pam_names, key="sb_pam_filter")
                    if pam_filter != "All":
                        partners_show = [p for p in partners if p.get("pam_name","").strip() == pam_filter]
                    else:
                        partners_show = partners
                else:
                    partners_show = partners
                for p in sorted(partners_show, key=lambda x: x.get("partner_name","")):
                    pn = p.get("partner_name","")
                    try: pct = float(p.get("percentage",0) or 0)
                    except: pct = 0
                    gl, gc = _grade(pct)
                    c1, c2, c3 = st.columns([3,1,1])
                    with c1:
                        if st.button(f"📋 {pn}", key=f"sb_view_{pn}", help=f"View scorecard for {pn}", use_container_width=True):
                            st.session_state["_view_partner"] = pn
                            st.session_state["current_page"] = "Step 2 — Score a Partner"
                            st.rerun()
                    with c2: st.markdown(f"<span style='color:{gc};font-weight:700;font-size:.85rem'>{gl}</span>", unsafe_allow_html=True)
                    with c3:
                        if st.button("🗑️", key=f"sb_del_{pn}", help=f"Delete {pn}"):
                            _delete_partner(pn)
                            st.rerun()
            else:
                st.caption("No partners scored yet.")

if chosen_cat=="All Metrics": visible_metrics=SCORECARD_METRICS
else:
    cn=chosen_cat.split("  ",1)[-1]
    ck=next(c["keys"] for c in CATEGORIES if c["label"]==cn)
    visible_metrics=[METRICS_BY_KEY[k] for k in ck]

if not active_tenant and page not in ("Admin — Manage Users","Admin — All Clients"):
    _brand()
    st.warning("No client selected. Use **Admin → Manage Users** to create a client account first.")
    st.stop()


# ═════════════════════════════════════════════════════════════════════════
# CLIENT INTAKE
# ═════════════════════════════════════════════════════════════════════════
if page=="Client Intake":
    _brand()
    st.markdown("""<div class="info-box">
    The <b>Partner Revenue Optimizer</b> is a structured process that will:
    <ol><li>Right-size the margins you provide to your partners, freeing up significant cash flow and revenues; and</li>
    <li>Lay the foundation for targeted partner marketing programs to drive more revenues.</li></ol>
    <p>An experienced channel consultant from <b>The York Group</b> will guide you through the process.
    Each metric is rated <b>1–5</b> (5 = best).</p></div>""",unsafe_allow_html=True)
    if st.session_state.get("_ci_saved"):
        st.markdown('<div class="toast">✅ Client information saved</div>',unsafe_allow_html=True); st.session_state["_ci_saved"]=False
    ci=st.session_state.get("client_info",{})
    with st.form("ci_form"):
        st.markdown('<div class="sec-head">📇 Client Contact Information</div>',unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            ci_name=st.text_input("Client name",value=ci.get("client_name",""),key="ci_name")
            ci_url=st.text_input("URL",value=ci.get("url",""),key="ci_url")
            saved_country=ci.get("country","")
            ci_country=st.selectbox("Country",COUNTRIES,index=COUNTRIES.index(saved_country) if saved_country in COUNTRIES else 0,key="ci_country")
            ci_phone=st.text_input("Primary phone",value=ci.get("phone",""),key="ci_phone")
        with c2:
            ci_pm=st.text_input("Client project manager",value=ci.get("project_manager",""),key="ci_pm")
            ci_city=st.text_input("City",value=ci.get("city",""),key="ci_city")
            ci_email=st.text_input("Primary contact email",value=ci.get("email",""),key="ci_email")
            ci_logo_url=st.text_input("Company logo URL",value=ci.get("logo_url",""),key="ci_logo_url",placeholder="https://example.com/logo.png")

        st.markdown('<div class="sec-head">🏢 Client Business Information</div>',unsafe_allow_html=True)
        st.markdown("**Company size — Number of employees**")
        sz_opts=["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]; saved_sz=ci.get("company_size",[]); sz_cols=st.columns(len(sz_opts)); sz_sel=[]
        for i,o in enumerate(sz_opts):
            with sz_cols[i]:
                if st.checkbox(o,value=o in saved_sz,key=f"ci_sz_{i}"): sz_sel.append(o)
        st.markdown("**Verticals**")
        v_opts=["Manufacturing","Automotive","Health care","Financial services","Retail","Government","Education","Media and entertainment","Professional services","Life sciences, pharmaceuticals","High-tech, electronics, communications, telecom","None - horizontal solution"]; saved_v=ci.get("verticals",[]); vc=st.columns(3); v_sel=[]
        for i,o in enumerate(v_opts):
            with vc[i%3]:
                if st.checkbox(o,value=o in saved_v,key=f"ci_v_{i}"): v_sel.append(o)
        other_v=st.text_input("Other verticals",value=ci.get("other_verticals",""),key="ci_ov")
        st.markdown("**Solution delivery**")
        d_opts=["On-premise","SaaS/PaaS","IaaS/VM","Device (HW+SW)"]; saved_d=ci.get("solution_delivery",[]); dc=st.columns(len(d_opts)); d_sel=[]
        for i,o in enumerate(d_opts):
            with dc[i]:
                if st.checkbox(o,value=o in saved_d,key=f"ci_d_{i}"): d_sel.append(o)

        st.markdown('<div class="sec-head">🎯 Target Customers</div>',unsafe_allow_html=True)
        st.markdown("**Target customer size — Number of employees**")
        tc_opts=["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]; saved_tc=ci.get("target_company_size",[]); tc_cols=st.columns(len(tc_opts)); tc_sel=[]
        for i,o in enumerate(tc_opts):
            with tc_cols[i]:
                if st.checkbox(o,value=o in saved_tc,key=f"ci_tc_{i}"): tc_sel.append(o)
        st.markdown("**Average first-year transaction value**")
        t_opts=["Under $1,000","$1,000–$10,000","$10,000–$50,000","$50,000–$100,000","More than $100,000"]; saved_t=ci.get("avg_transaction_value","")
        txn=st.selectbox("Select range",t_opts,index=t_opts.index(saved_t) if saved_t in t_opts else 0,key="ci_txn")

        st.markdown('<div class="sec-head">📊 Channel Information</div>',unsafe_allow_html=True)
        st.markdown("**Services as % of license/subscription**")
        s_opts=["No services","<20%","20–50%","50–200%",">200%"]; saved_s=ci.get("services_pct","")
        svc=st.selectbox("Select range",s_opts,index=s_opts.index(saved_s) if saved_s in s_opts else 0,key="ci_svc")
        svc_c=st.text_input("Comments",value=ci.get("services_comments",""),key="ci_svc_c")
        st.markdown("**How many resellers/channel partners do you have?**")
        p_opts=["<100","100-200","200-500","500-1,000","1,000-5,000",">5,000"]; saved_p=ci.get("partner_count","")
        pc=st.selectbox("Select range",p_opts,index=p_opts.index(saved_p) if saved_p in p_opts else 0,key="ci_pc")
        st.markdown("**% revenues from indirect channels**")
        i_opts=["<10%","10-30%","30-50%",">50%"]; saved_i=ci.get("indirect_revenue_pct","")
        ind=st.selectbox("Select range",i_opts,index=i_opts.index(saved_i) if saved_i in i_opts else 0,key="ci_ind")
        st.markdown("**Discounts to partners**")
        disc_opts=["<15%","15-30%","30-50%",">60%","Other"]; saved_disc=ci.get("discounts",[]); disc_c=st.columns(len(disc_opts)); disc_sel=[]
        for i,o in enumerate(disc_opts):
            with disc_c[i]:
                if st.checkbox(o,value=o in saved_disc,key=f"ci_disc_{i}"): disc_sel.append(o)
        st.markdown("**Partner designations**")
        desig=st.text_input("Comma-separated, e.g. gold, silver, bronze",value=ci.get("partner_designations",""),key="ci_desig")
        st.markdown("---")
        _,cr=st.columns([3,1])
        with cr: ci_sub=st.form_submit_button("Next →  Step 1",use_container_width=True,type="primary")
    if ci_sub:
        st.session_state["client_info"]={"client_name":ci_name,"project_manager":ci_pm,"url":ci_url,"city":ci_city,"country":ci_country,"email":ci_email,"phone":ci_phone,"logo_url":ci_logo_url,"company_size":sz_sel,"verticals":v_sel,"other_verticals":other_v,"solution_delivery":d_sel,"target_company_size":tc_sel,"avg_transaction_value":txn,"services_pct":svc,"services_comments":svc_c,"partner_count":pc,"indirect_revenue_pct":ind,"discounts":disc_sel,"partner_designations":desig}
        _client_path().write_text(json.dumps(st.session_state["client_info"],indent=2))
        st.session_state["_ci_saved"]=True; st.session_state["current_page"]="Step 1 — Scoring Criteria"; st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# STEP 1 — SCORING CRITERIA
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 1 — Scoring Criteria":
    _brand()
    st.markdown("## Step 1 — Define Scoring Criteria")
    st.markdown("Configure **1–5** thresholds. Toggle metrics on/off. Changes apply retroactively to all scored partners.")
    if st.session_state.get("_p1_saved"):
        st.markdown('<div class="toast">✅ Criteria saved — all partners re-scored</div>',unsafe_allow_html=True); st.session_state["_p1_saved"]=False
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
        _save_criteria(); st.session_state["_p1_saved"]=True
        if p1n: st.session_state["current_page"]="Step 2 — Score a Partner"
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# STEP 2 — SCORE A PARTNER
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 2 — Score a Partner":
    _brand()
    st.markdown("## Step 2 — Score a Partner")
    if not _save_path().exists():
        st.warning("⚠️ Complete **Step 1** first."); st.stop()
    st.session_state["criteria"]=json.loads(_save_path().read_text())
    cr=st.session_state["criteria"]; em=_enabled(); mx=len(em)*5
    # Form version counter — incremented on submit to clear all fields
    if "p2_ver" not in st.session_state: st.session_state["p2_ver"]=0
    fv=st.session_state["p2_ver"]
    # Edit mode: if a partner was clicked in sidebar or assessment
    view_pn = st.session_state.pop("_view_partner", None)
    view_raw = None
    is_edit = False
    if view_pn:
        raw_all = _load_raw()
        view_raw = next((r for r in raw_all if r.get("partner_name") == view_pn), None)
        if view_raw:
            is_edit = True
            st.info(f"✏️ Editing scorecard for **{view_pn}** — make changes and click **Save Changes**")
    if st.session_state.get("_p2_submitted"):
        st.markdown('<div class="toast">✅ Partner submitted & saved. Ready for next partner.</div>',unsafe_allow_html=True); st.session_state["_p2_submitted"]=False
    if st.session_state.get("_p2_updated"):
        st.markdown('<div class="toast">✅ Partner scorecard updated successfully.</div>',unsafe_allow_html=True); st.session_state["_p2_updated"]=False
    st.markdown(f"Total out of **{mx}** ({len(em)} metrics × 5).")
    st.markdown('<div class="partner-hdr">Partner details</div>',unsafe_allow_html=True)
    tiers=_tiers(); t_opts=["Please choose..."]+tiers if tiers else ["Please choose...","(Set tiers in Client Intake)"]
    pc1,pc2,pc3,pc4=st.columns(4)
    with pc1: pn=st.text_input("Partner company name",key=f"p2_pn_{fv}",placeholder="e.g. ABC reseller",value=view_raw.get("partner_name","") if view_raw else "")
    with pc2: p_yr=st.text_input("Year became partner",key=f"p2_py_{fv}",placeholder="e.g. 2020",value=view_raw.get("partner_year","") if view_raw else "")
    with pc3:
        tier_val = view_raw.get("partner_tier","") if view_raw else ""
        pt=st.selectbox("Tier",t_opts,index=t_opts.index(tier_val) if tier_val in t_opts else 0,key=f"p2_pt_{fv}")
    with pc4:
        p_disc=st.text_input("Partner Discount",key=f"p2_disc_{fv}",placeholder="e.g. 20%",value=view_raw.get("partner_discount","") if view_raw else "")
    pc5,pc6=st.columns(2)
    with pc5: pcity=st.text_input("City",key=f"p2_city_{fv}",placeholder="e.g. Paris",value=view_raw.get("partner_city","") if view_raw else "")
    with pc6:
        country_val = view_raw.get("partner_country","") if view_raw else ""
        pcountry=st.selectbox("Country",COUNTRIES,index=COUNTRIES.index(country_val) if country_val in COUNTRIES else 0,key=f"p2_country_{fv}")
    pam1,pam2=st.columns(2)
    with pam1: pam_name=st.text_input("Partner Account Manager (PAM) name",key=f"p2_pam_name_{fv}",placeholder="e.g. Jane Smith",value=view_raw.get("pam_name","") if view_raw else "")
    with pam2: pam_email=st.text_input("PAM email",key=f"p2_pam_email_{fv}",placeholder="e.g. jane@company.com",value=view_raw.get("pam_email","") if view_raw else "")
    st.markdown("---")
    if chosen_cat=="All Metrics": ve=em
    else:
        cn=chosen_cat.split("  ",1)[-1]; ck=next(c["keys"] for c in CATEGORIES if c["label"]==cn); ve=[m for m in em if m["key"] in ck]
    for m in ve:
        mk=m["key"]; mc=cr[mk]; iq=m["type"]=="quantitative"
        tt='<span class="tag tag-q">Quantitative</span>' if iq else '<span class="tag tag-ql">Qualitative</span>'
        dt=f'<span class="tag {"tag-hi" if m["direction"]=="higher_is_better" else "tag-lo"}">{"↑ Higher" if m["direction"]=="higher_is_better" else "↓ Lower"} is better</span>'
        st.markdown(f'<div class="mc"><span class="mname">{m["id"]}. {m["name"]}</span>{tt}{dt}<div class="mexpl">{m["explanation"]}</div></div>',unsafe_allow_html=True)
        view_val = view_raw.get(f"raw_{mk}","") if view_raw else ""
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
            with ic: pv=st.text_input(f"Value ({u})",key=f"p2_{mk}_{fv}",placeholder=f"Enter number ({u})",label_visibility="collapsed",value=str(view_val) if view_val else "")
            scr=calc_score(mk,pv)
        else:
            opts=["— Select —"]+[f"({s}) {mc['descriptors'][s]}" for s in("1","2","3","4","5")]
            # Pre-select for edit mode
            view_idx = 0
            if view_val:
                for oi, o in enumerate(opts):
                    if view_val in o: view_idx = oi; break
            ic,sc_c=st.columns([4,1])
            with ic: pv=st.selectbox("Level",opts,index=view_idx,key=f"p2_{mk}_{fv}",label_visibility="collapsed")
            if pv and pv!="— Select —": raw_d=re.sub(r"^\(\d\)\s*","",pv); scr=calc_score(mk,raw_d)
            else: scr=None
        with sc_c:
            if scr: st.markdown(f'<div class="live-score" style="background:{SC[scr]}">{scr}</div>',unsafe_allow_html=True)
            else: st.markdown('<div class="live-score" style="background:#ccc">—</div>',unsafe_allow_html=True)
    # Summary
    st.markdown("---")
    full={}; raw_vals={}
    for m in em:
        mk=m["key"]; pv=st.session_state.get(f"p2_{mk}_{fv}","")
        if not pv or pv=="— Select —":
            full[mk]=None; raw_vals[mk]=None
        elif m["type"]=="qualitative" and isinstance(pv,str) and pv.startswith("("):
            raw_d=re.sub(r"^\(\d\)\s*","",pv); full[mk]=calc_score(mk,raw_d); raw_vals[mk]=raw_d
        else:
            full[mk]=calc_score(mk,pv); raw_vals[mk]=pv
    si={k:v for k,v in full.items() if v is not None}; total=sum(si.values()); sn=len(si); mp=sn*5
    pct=(total/mp*100) if mp else 0; gl,gc=_grade(pct); pname=st.session_state.get(f"p2_pn_{fv}","Partner") or "Partner"
    st.markdown(f"### Live Summary — {pname}")
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f'<div class="sum-card"><div class="sum-big">{total}</div><div class="sum-lbl">Total</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sum-card"><div class="sum-big">{sn}/{len(em)}</div><div class="sum-lbl">Scored</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="sum-card"><div class="sum-big">{pct:.1f}%</div><div class="sum-lbl">Percentage</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:{gc}">{gl}</div><div class="sum-lbl">Grade</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    # Build row + raw dicts (shared by both submit and save)
    def _build_row_raw():
        row={"partner_name":pname,"partner_year":st.session_state.get(f"p2_py_{fv}",""),
             "partner_tier":st.session_state.get(f"p2_pt_{fv}",""),
             "partner_discount":st.session_state.get(f"p2_disc_{fv}",""),
             "partner_city":st.session_state.get(f"p2_city_{fv}",""),
             "partner_country":st.session_state.get(f"p2_country_{fv}",""),
             "pam_name":st.session_state.get(f"p2_pam_name_{fv}",""),
             "pam_email":st.session_state.get(f"p2_pam_email_{fv}",""),
             "total_score":total,"max_possible":mp,"percentage":round(pct,1)}
        for m in em: row[m["key"]]=full.get(m["key"],"")
        raw_dict={"partner_name":pname,"partner_year":st.session_state.get(f"p2_py_{fv}",""),
                  "partner_tier":st.session_state.get(f"p2_pt_{fv}",""),
                  "partner_discount":st.session_state.get(f"p2_disc_{fv}",""),
                  "partner_city":st.session_state.get(f"p2_city_{fv}",""),
                  "partner_country":st.session_state.get(f"p2_country_{fv}",""),
                  "pam_name":st.session_state.get(f"p2_pam_name_{fv}",""),
                  "pam_email":st.session_state.get(f"p2_pam_email_{fv}","")}
        for m in em: raw_dict[f"raw_{m['key']}"]=raw_vals.get(m["key"])
        return row, raw_dict
    if is_edit:
        # Edit mode — update existing partner
        _,_,save_col=st.columns([2,2,1])
        with save_col:
            if st.button("💾  Save Changes",use_container_width=True,type="primary"):
                if not pname or pname=="Partner":
                    st.error("Partner name is missing.")
                else:
                    row, raw_dict = _build_row_raw()
                    _upsert_partner(row, raw_dict)
                    st.session_state["_p2_updated"]=True; st.rerun()
    else:
        # New partner mode
        _,_,submit_col=st.columns([2,2,1])
        with submit_col:
            if st.button("✅  Submit & Start New Partner",use_container_width=True,type="primary"):
                if not pname or pname=="Partner":
                    st.error("Enter a partner name first.")
                elif _partner_exists(pname):
                    st.error(f"A partner named **{pname}** already exists. Use a unique name.")
                elif _max_partners() and _partner_count() >= _max_partners():
                    st.error(f"Partner limit reached (**{_max_partners()}**). Contact your admin to increase the limit.")
                else:
                    row, raw_dict = _build_row_raw()
                    _append_partner(row, raw_dict)
                    st.session_state["p2_ver"]=fv+1
                    st.session_state["_p2_submitted"]=True; st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# STEP 3 — PARTNER ASSESSMENT
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 3 — Partner Assessment":
    _brand(); st.markdown("## Step 3 — Partner Assessment")
    partners=_load_partners(); em=_enabled()
    if not partners: st.info("No partners scored yet. Complete **Step 2**."); st.stop()

    # ── Filters row ──
    f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
    with f1:
        search_q = st.text_input("🔍 Search partner", key="p3_search", placeholder="Type to search...")
    with f2:
        pam_names = sorted(set(p.get("pam_name","").strip() for p in partners if p.get("pam_name","").strip()))
        pam_f = st.selectbox("Filter by PAM", ["All PAMs"] + pam_names, key="p3_pam_filter")
    with f3:
        sort_opts = ["Score (highest first)", "Score (lowest first)", "Partner (A–Z)", "Partner (Z–A)", "PAM (A–Z)"]
        sort_by = st.selectbox("Sort by", sort_opts, key="p3_sort")
    with f4:
        metric_filter_opts = ["All metrics"] + [m["name"] for m in em]
        metric_filter = st.selectbox("Filter by metric score", metric_filter_opts, key="p3_metric_filter")

    # ── Apply filters ──
    ps = list(partners)
    if search_q:
        sq = search_q.strip().lower()
        ps = [p for p in ps if sq in p.get("partner_name","").lower() or sq in p.get("pam_name","").lower() or sq in p.get("partner_country","").lower()]
    if pam_f != "All PAMs":
        ps = [p for p in ps if p.get("pam_name","").strip() == pam_f]

    # Metric value filter: if a specific metric is selected, filter to partners who have a score for it
    filter_mk = None
    if metric_filter != "All metrics":
        filter_mk = next((m["key"] for m in em if m["name"] == metric_filter), None)

    # ── Sort ──
    if sort_by == "Score (highest first)":
        ps = sorted(ps, key=lambda p: -int(p.get("total_score",0) or 0))
    elif sort_by == "Score (lowest first)":
        ps = sorted(ps, key=lambda p: int(p.get("total_score",0) or 0))
    elif sort_by == "Partner (A–Z)":
        ps = sorted(ps, key=lambda p: p.get("partner_name","").lower())
    elif sort_by == "Partner (Z–A)":
        ps = sorted(ps, key=lambda p: p.get("partner_name","").lower(), reverse=True)
    elif sort_by == "PAM (A–Z)":
        ps = sorted(ps, key=lambda p: p.get("pam_name","").lower())

    # If filtering by specific metric, sort by that metric's value
    if filter_mk:
        ps = sorted(ps, key=lambda p: -int(p.get(filter_mk,"") or 0))

    st.markdown(f"**{len(ps)}** partners, **{len(em)}** metrics.")

    # ── Build heatmap table (with Country column and clickable names) ──
    hdr="<tr><th>Rank</th><th style='text-align:left'>Partner</th><th>Country</th><th>Tier</th><th>PAM</th>"
    for m in em: hdr+=f'<th class="hm-diag" title="{m["name"]}"><div>{m["name"][:25]}</div></th>'
    hdr+="<th>Total</th><th>%</th></tr>"
    rows=""
    for ri,p in enumerate(ps,1):
        pn_display = p.get('partner_name','')
        rows+=f"<tr><td><b>{ri}</b></td><td style='text-align:left;padding-left:10px;white-space:nowrap'>{pn_display}</td><td style='white-space:nowrap'>{p.get('partner_country','')}</td><td>{p.get('partner_tier','')}</td><td style='white-space:nowrap'>{p.get('pam_name','')}</td>"
        for m in em:
            try: v=int(p.get(m["key"],"") or 0)
            except: v=None
            if v and 1<=v<=5: rows+=f'<td class="hm{v}">{v}</td>'
            else: rows+='<td style="color:#ccc">—</td>'
        try: tv=int(p.get("total_score",0) or 0)
        except: tv=0
        try: pv=float(p.get("percentage",0) or 0)
        except: pv=0
        rows+=f'<td class="hm-total">{tv}</td><td class="hm-total">{pv:.1f}%</td></tr>'
    st.markdown(f'<div class="scroll-tbl"><table class="hm-tbl"><thead>{hdr}</thead><tbody>{rows}</tbody></table></div>',unsafe_allow_html=True)

    # ── Clickable partner access ──
    st.markdown("---")
    st.markdown("#### 📋 Open Partner Scorecard")
    partner_names_sorted = [p.get("partner_name","") for p in ps]
    if partner_names_sorted:
        oc1, oc2 = st.columns([3, 1])
        with oc1:
            open_pn = st.selectbox("Select a partner to view/edit their scorecard", partner_names_sorted, key="p3_open_partner")
        with oc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✏️  Open Scorecard", use_container_width=True, type="primary", key="p3_open_btn"):
                st.session_state["_view_partner"] = open_pn
                st.session_state["current_page"] = "Step 2 — Score a Partner"
                st.rerun()

    st.markdown("---")
    xb=_gen_xlsx(ps,em)
    if xb: st.download_button("⬇️  Download Excel",xb,"Partner_Assessment.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary")
    if _csv_path().exists(): st.download_button("⬇️  Download CSV",_csv_path().read_text(),"all_partners.csv","text/csv")


# ═════════════════════════════════════════════════════════════════════════
# STEP 4 — PARTNER CLASSIFICATION (3 quadrants + Long Tail)
# ═════════════════════════════════════════════════════════════════════════
elif page=="Step 4 — Partner Classification":
    _brand(); st.markdown("## Step 4 — Partner Classification")
    partners=_load_partners(); em=_enabled(); em_keys={m["key"] for m in em}
    if not partners: st.info("No partners scored yet. Complete **Step 2** first."); st.stop()
    st.markdown("""<div class="info-box">Classify partners into <b>three quadrants</b> plus <b>Long Tail</b>. Partners that don't match Q1–Q3 criteria are automatically classified as Long Tail.<br>Levels: <b>High</b> ≥ 4, <b>Mid</b> = 3, <b>Low</b> ≤ 2, <b>Any</b> = score &gt; 0. First match wins (1 → 3).</div>""",unsafe_allow_html=True)
    q_config=_load_q_config()
    if "q_config" not in st.session_state: st.session_state["q_config"]=q_config
    if st.session_state.get("_q_saved"):
        st.markdown('<div class="toast">✅ Classification saved & applied</div>',unsafe_allow_html=True); st.session_state["_q_saved"]=False
    st.markdown("### Define Quadrant Criteria")
    metric_options=["(none)"]+[m["name"] for m in SCORECARD_METRICS]; level_options=["high","mid","low","any"]; MAX_C=6
    with st.form("class_form"):
        new_config={}
        for qn in(1,2,3):
            ql,qc=Q_LABELS.get(qn,(f"Q{qn}","#666"))
            st.markdown(f'<div style="display:flex;align-items:center;margin:18px 0 8px;"><div class="q-badge" style="background:{qc}">{qn}</div><b style="font-size:1.05rem">{ql}</b></div>',unsafe_allow_html=True)
            st.caption(Q_DESCS.get(qn,""))
            current=st.session_state["q_config"].get(qn,[])
            crit_list=[]
            for ci in range(MAX_C):
                if ci<len(current): cur_key,cur_level=current[ci]; cur_mn=next((m["name"] for m in SCORECARD_METRICS if m["key"]==cur_key),"(none)"); cur_li=level_options.index(cur_level) if cur_level in level_options else 0
                else: cur_mn="(none)"; cur_li=0
                mc,lc=st.columns([3,1])
                with mc: sel_m=st.selectbox(f"Q{qn}M{ci+1}",metric_options,index=metric_options.index(cur_mn) if cur_mn in metric_options else 0,key=f"q{qn}_m{ci}",label_visibility="collapsed")
                with lc: sel_l=st.selectbox(f"Q{qn}L{ci+1}",level_options,index=cur_li,key=f"q{qn}_l{ci}",label_visibility="collapsed")
                if sel_m!="(none)":
                    mk=next((m["key"] for m in SCORECARD_METRICS if m["name"]==sel_m),None)
                    if mk: crit_list.append((mk,sel_l))
            new_config[qn]=crit_list
        st.markdown(f'<div style="display:flex;align-items:center;margin:18px 0 8px;"><div class="q-badge" style="background:#dc4040">4</div><b style="font-size:1.05rem">Long Tail</b></div>',unsafe_allow_html=True)
        st.caption("Automatically assigned to partners that don't match Q1–Q3 criteria.")
        st.markdown("---"); _,cc=st.columns([3,1])
        with cc: q_sub=st.form_submit_button("💾  Save & Classify",use_container_width=True,type="primary")
    if q_sub:
        st.session_state["q_config"]=new_config; _save_q_config(new_config); st.session_state["_q_saved"]=True; st.rerun()
    st.markdown("---"); st.markdown("### Classification Results")
    ac=st.session_state["q_config"]; classification=classify_partners(partners,ac,em_keys)
    if not classification: st.info("No partners to classify."); st.stop()
    by_q={1:[],2:[],3:[],4:[]}
    for pn,qn in classification.items(): by_q.setdefault(qn,[]).append(pn)
    for qn in(1,2,3,4):
        ql,qc=Q_LABELS.get(qn,(f"Q{qn}","#666")); members=by_q.get(qn,[]); cnt=len(members)
        if qn<=3:
            cp=[]
            for(mk,lvl) in ac.get(qn,[]):
                mn=next((m["name"] for m in SCORECARD_METRICS if m["key"]==mk),mk); cp.append(f"{mn} = <b>{lvl}</b>")
            ch=" &nbsp;·&nbsp; ".join(cp) if cp else "<i>No criteria</i>"
        else:
            ch="<i>Does not match Q1–Q3 criteria</i>"
        ph="".join(f'<span class="q-partner">{n}</span>' for n in members) if members else '<span style="color:#999">None</span>'
        st.markdown(f'<div class="q-card" style="border-color:{qc}20;background:{qc}08;"><div style="display:flex;align-items:center;"><div class="q-badge" style="background:{qc}">{qn}</div><h4 style="margin:0;color:{qc}">{ql}</h4><span style="margin-left:auto;font-size:1.4rem;font-weight:800;color:{qc};font-family:\'JetBrains Mono\',monospace">{cnt}</span></div><div class="q-criteria">Criteria: {ch}</div><div style="margin-top:10px">{ph}</div></div>',unsafe_allow_html=True)
    st.markdown("### Full Classification Table")
    tbl="<table class='hm-tbl'><thead><tr><th>Partner</th><th>Total</th><th>%</th><th>Q</th><th>Classification</th></tr></thead><tbody>"
    sc=sorted(classification.items(),key=lambda x:(x[1],-next((int(p.get("total_score",0) or 0) for p in partners if p.get("partner_name")==x[0]),0)))
    for pn,qn in sc:
        p=next((p for p in partners if p.get("partner_name")==pn),{})
        try: tv=int(p.get("total_score",0) or 0)
        except: tv=0
        try: pv=float(p.get("percentage",0) or 0)
        except: pv=0
        ql,qc=Q_LABELS.get(qn,(f"Q{qn}","#666"))
        tbl+=f'<tr><td style="text-align:left;padding-left:10px;font-weight:600">{pn}</td><td>{tv}</td><td>{pv:.1f}%</td><td><span class="score-pill" style="background:{qc}">{qn}</span></td><td style="color:{qc};font-weight:700">{ql}</td></tr>'
    tbl+="</tbody></table>"
    st.markdown(tbl,unsafe_allow_html=True)
    st.markdown("---")
    # Downloads: Excel, CSV, JSON
    dl1, dl2, dl3 = st.columns(3)
    # Build classification data for export
    class_rows = []
    for pn, qn in sorted(classification.items(), key=lambda x: (x[1], x[0])):
        p = next((p for p in partners if p.get("partner_name") == pn), {})
        try: tv = int(p.get("total_score", 0) or 0)
        except: tv = 0
        try: pv = float(p.get("percentage", 0) or 0)
        except: pv = 0
        ql, _ = Q_LABELS.get(qn, (f"Q{qn}", "#666"))
        class_rows.append({"Partner": pn, "Total Score": tv, "Percentage": round(pv, 1),
                           "Quadrant": qn, "Classification": ql,
                           "Tier": p.get("partner_tier", ""), "PAM": p.get("pam_name", "")})
    with dl1:
        # Excel
        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Classification"
            q_fills = {1: PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid"),
                       2: PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
                       3: PatternFill(start_color="FFFFCC", end_color="FFFFCC", fill_type="solid"),
                       4: PatternFill(start_color="FA7A7A", end_color="FA7A7A", fill_type="solid")}
            hf = PatternFill(start_color="1E2A3A", end_color="1E2A3A", fill_type="solid")
            hfont = Font(color="FFFFFF", bold=True, size=10)
            bdr = Border(left=Side(style="thin", color="CCCCCC"), right=Side(style="thin", color="CCCCCC"),
                         top=Side(style="thin", color="CCCCCC"), bottom=Side(style="thin", color="CCCCCC"))
            headers = ["Partner", "Tier", "PAM", "Total Score", "Percentage", "Quadrant", "Classification"]
            for ci, h in enumerate(headers, 1):
                cell = ws.cell(1, ci, h); cell.fill = hf; cell.font = hfont; cell.border = bdr
                cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions["A"].width = 28; ws.column_dimensions["B"].width = 14
            ws.column_dimensions["C"].width = 22; ws.column_dimensions["G"].width = 24
            for ri, r in enumerate(class_rows, 2):
                ws.cell(ri, 1, r["Partner"]).border = bdr
                ws.cell(ri, 2, r["Tier"]).border = bdr
                ws.cell(ri, 3, r["PAM"]).border = bdr
                ws.cell(ri, 4, r["Total Score"]).border = bdr; ws.cell(ri, 4).alignment = Alignment(horizontal="center")
                pc = ws.cell(ri, 5); pc.value = r["Percentage"] / 100; pc.number_format = "0.0%"; pc.border = bdr; pc.alignment = Alignment(horizontal="center")
                qc = ws.cell(ri, 6, r["Quadrant"]); qc.border = bdr; qc.alignment = Alignment(horizontal="center")
                qc.fill = q_fills.get(r["Quadrant"], PatternFill())
                ws.cell(ri, 7, r["Classification"]).border = bdr; ws.cell(ri, 7).font = Font(bold=True)
            buf = io.BytesIO(); wb.save(buf)
            st.download_button("⬇️  Download Excel", buf.getvalue(), "Partner_Classification.xlsx",
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
        except ImportError:
            st.warning("openpyxl required for Excel export")
    with dl2:
        # CSV
        csv_buf = io.StringIO()
        if class_rows:
            cw = csv.DictWriter(csv_buf, fieldnames=list(class_rows[0].keys()))
            cw.writeheader()
            for r in class_rows: cw.writerow(r)
        st.download_button("⬇️  Download CSV", csv_buf.getvalue(), "Partner_Classification.csv", "text/csv")
    with dl3:
        st.download_button("⬇️  Download JSON", json.dumps(classification, indent=2), "partner_classification.json", "application/json")


# ═════════════════════════════════════════════════════════════════════════
# IMPORT DATA — CSV upload + column mapping → batch partner creation
# ═════════════════════════════════════════════════════════════════════════
elif page=="Import Data":
    _brand(); st.markdown("## Import Partner Data from CSV")
    if not _save_path().exists():
        st.warning("⚠️ Complete **Step 1 — Scoring Criteria** first so metrics are available for mapping."); st.stop()
    st.session_state["criteria"] = json.loads(_save_path().read_text())
    cr = st.session_state["criteria"]; em = _enabled()

    st.markdown("""<div class="info-box">
    Upload a CSV exported from your CRM, ERP, or PRM system. Map its columns to ChannelPRO scoring metrics
    and import partners in bulk. Existing partners (matched by name) will be <b>updated</b>; new names will
    be <b>created</b>. Unmapped metrics are left blank for manual scoring later.</div>""", unsafe_allow_html=True)

    # Show import results from previous run
    if st.session_state.get("_import_done"):
        res = st.session_state.pop("_import_done")
        st.markdown(f'<div class="toast">✅ Import complete — {res["created"]} created, {res["updated"]} updated, {res["errors"]} errors</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("📁 Upload CSV file", type=["csv"], key="import_csv")
    if uploaded is None:
        st.info("Upload a CSV to get started. Required column: **Partner** (name or ID)."); st.stop()

    # Parse CSV
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Could not read CSV: {e}"); st.stop()
    if df.empty:
        st.error("The uploaded CSV is empty."); st.stop()

    csv_cols = list(df.columns)
    st.markdown("### 📄 CSV Preview (first 5 rows)")
    st.dataframe(df.head(5), use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} rows × {len(csv_cols)} columns")

    # ── Mapping interface ──
    st.markdown("---")
    st.markdown("### 🔗 Column Mapping")
    none_opt = ["— None —"]

    # Helper: find best auto-match for a label among CSV columns
    def _auto_match(label, cols):
        ll = label.lower()
        for c in cols:
            if c.lower().strip() == ll: return c
        for c in cols:
            if ll in c.lower() or c.lower() in ll: return c
        return None

    # ── Required: Partner name column ──
    st.markdown('<div class="sec-head">🏢 Required</div>', unsafe_allow_html=True)
    auto_pn = _auto_match("partner", csv_cols) or _auto_match("partner name", csv_cols) or _auto_match("company", csv_cols)
    partner_col = st.selectbox("Partner name column **(required)**",
        csv_cols, index=csv_cols.index(auto_pn) if auto_pn else 0, key="imp_partner_col")

    # ── Optional: partner detail fields ──
    st.markdown('<div class="sec-head">📇 Partner Details (optional)</div>', unsafe_allow_html=True)
    detail_fields = [
        ("Year became partner", "partner_year", ["year","since","partner year","start year"]),
        ("Tier", "partner_tier", ["tier","level","designation"]),
        ("City", "partner_city", ["city"]),
        ("Country", "partner_country", ["country"]),
        ("PAM name", "pam_name", ["pam","pam name","account manager","partner manager"]),
        ("PAM email", "pam_email", ["pam email","manager email"]),
    ]
    dc1, dc2, dc3 = st.columns(3)
    detail_mapping = {}
    for i, (label, field, hints) in enumerate(detail_fields):
        auto = None
        for h in hints:
            auto = _auto_match(h, csv_cols)
            if auto: break
        col_widget = [dc1, dc2, dc3][i % 3]
        with col_widget:
            sel = st.selectbox(label, none_opt + csv_cols,
                index=(csv_cols.index(auto) + 1) if auto and auto in csv_cols else 0,
                key=f"imp_det_{field}")
        if sel != "— None —":
            detail_mapping[field] = sel

    # ── Metric mapping ──
    st.markdown('<div class="sec-head">📊 Scoring Metrics</div>', unsafe_allow_html=True)
    st.caption("Map CSV columns to each metric. For quantitative metrics, the raw value from CSV will be auto-scored using your Step 1 ranges.")
    metric_mapping = {}
    mc1, mc2 = st.columns(2)
    for idx, m in enumerate(em):
        auto = _auto_match(m["name"], csv_cols)
        col_widget = mc1 if idx % 2 == 0 else mc2
        with col_widget:
            mtype = "📏" if m["type"] == "quantitative" else "📝"
            sel = st.selectbox(f'{mtype} {m["name"]}', none_opt + csv_cols,
                index=(csv_cols.index(auto) + 1) if auto and auto in csv_cols else 0,
                key=f"imp_m_{m['key']}")
        if sel != "— None —":
            metric_mapping[m["key"]] = sel

    # Summary
    st.markdown("---")
    mapped_count = len(metric_mapping)
    st.markdown(f"**Mapped:** {mapped_count}/{len(em)} metrics  •  Partner column: **{partner_col}**")
    if mapped_count == 0:
        st.caption("ℹ️ No metrics mapped — partners will be created with blank scores for manual entry.")

    # ── Process import ──
    st.markdown("---")
    _, _, btn_col = st.columns([2, 2, 1])
    with btn_col:
        do_import = st.button("📥  Import Partners", use_container_width=True, type="primary")

    if do_import:
        created = 0; updated = 0; error_rows = []; skipped_limit = 0
        existing_names = {p.get("partner_name","").strip().lower() for p in _load_partners()}
        max_p = _max_partners(); current_count = len(existing_names)
        progress = st.progress(0, text="Importing...")

        for row_idx, row in df.iterrows():
            progress.progress(min((row_idx + 1) / len(df), 1.0), text=f"Processing row {row_idx + 1}/{len(df)}...")
            pname = str(row.get(partner_col, "")).strip()
            if not pname or pname.lower() in ("nan", "none", ""):
                error_rows.append({"row": row_idx + 2, "partner": pname, "error": "Missing partner name"})
                continue

            # Check partner limit for new partners (updates are always allowed)
            is_new = pname.strip().lower() not in existing_names
            if is_new and max_p and (current_count + created) >= max_p:
                skipped_limit += 1
                error_rows.append({"row": row_idx + 2, "partner": pname, "error": f"Partner limit ({max_p}) reached"})
                continue

            # Build raw dict
            raw_dict = {"partner_name": pname}
            for field, csv_col in detail_mapping.items():
                raw_dict[field] = str(row.get(csv_col, "")).strip()
                if raw_dict[field].lower() == "nan": raw_dict[field] = ""

            # Build scored dict
            row_dict = {"partner_name": pname}
            for field in ["partner_year","partner_tier","partner_city","partner_country","pam_name","pam_email"]:
                row_dict[field] = raw_dict.get(field, "")

            scores = {}; raw_vals = {}
            for m in em:
                mk = m["key"]
                if mk in metric_mapping:
                    raw_val = row.get(metric_mapping[mk])
                    if pd.isna(raw_val) or str(raw_val).strip().lower() in ("", "nan", "none", "n/a"):
                        raw_vals[mk] = None; scores[mk] = None
                    else:
                        raw_str = str(raw_val).strip()
                        raw_vals[mk] = raw_str
                        raw_dict[f"raw_{mk}"] = raw_str
                        scr = calc_score(mk, raw_str, cr)
                        scores[mk] = scr
                        row_dict[mk] = scr if scr else ""
                else:
                    raw_vals[mk] = None; scores[mk] = None
                    row_dict[mk] = ""

            # Calculate totals
            si = {k: v for k, v in scores.items() if v is not None}
            total = sum(si.values()); sn = len(si); mp = sn * 5
            pct = round(total / mp * 100, 1) if mp else 0
            row_dict["total_score"] = total
            row_dict["max_possible"] = mp
            row_dict["percentage"] = pct

            # Upsert
            try:
                is_update = not is_new
                _upsert_partner(row_dict, raw_dict)
                if is_update:
                    updated += 1
                else:
                    created += 1
                    existing_names.add(pname.strip().lower())
            except Exception as e:
                error_rows.append({"row": row_idx + 2, "partner": pname, "error": str(e)})

        progress.empty()

        # Show results
        st.session_state["_import_done"] = {"created": created, "updated": updated, "errors": len(error_rows)}

        st.markdown("### ✅ Import Results")
        r1, r2, r3 = st.columns(3)
        with r1: st.metric("Created", created)
        with r2: st.metric("Updated", updated)
        with r3: st.metric("Errors", len(error_rows))

        if skipped_limit > 0:
            st.warning(f"⚠️ **{skipped_limit}** partner(s) skipped — partner limit of **{max_p}** reached. Contact your admin to increase the limit.")

        if error_rows:
            st.markdown("#### ⚠️ Errors")
            err_df = pd.DataFrame(error_rows)
            st.dataframe(err_df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Errors CSV", err_df.to_csv(index=False),
                "import_errors.csv", "text/csv")

        if created > 0 or updated > 0:
            st.success(f"Successfully imported **{created + updated}** partners. View them on the **Partner List** page or in **Step 3**.")


# ═════════════════════════════════════════════════════════════════════════
# PARTNER LIST — sortable table + inline edit + manual add
# ═════════════════════════════════════════════════════════════════════════
elif page=="Partner List":
    _brand(); st.markdown("## Partner List")
    if not _save_path().exists():
        st.warning("⚠️ Complete **Step 1 — Scoring Criteria** first."); st.stop()
    st.session_state["criteria"] = json.loads(_save_path().read_text())
    cr = st.session_state["criteria"]; em = _enabled()
    partners = _load_partners()

    # ── Edit mode (single partner) ──
    edit_pn = st.session_state.get("_pl_edit")
    if edit_pn:
        raw_all = _load_raw()
        raw_p = next((r for r in raw_all if r.get("partner_name") == edit_pn), None)
        csv_p = next((p for p in partners if p.get("partner_name") == edit_pn), None)
        if not csv_p:
            st.error(f"Partner '{edit_pn}' not found."); st.session_state.pop("_pl_edit", None); st.rerun()

        if st.button("← Back to Partner List", key="pl_back"):
            st.session_state.pop("_pl_edit", None); st.rerun()

        st.markdown(f"### ✏️ Edit Scorecard — {edit_pn}")

        # Show save confirmation
        if st.session_state.get("_pl_edit_saved"):
            st.markdown('<div class="toast">✅ Partner scorecard updated</div>', unsafe_allow_html=True)
            st.session_state["_pl_edit_saved"] = False

        with st.form("pl_edit_form"):
            # Partner details
            st.markdown('<div class="sec-head">📇 Partner Details</div>', unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1:
                ed_name = st.text_input("Partner name", value=edit_pn, key="ple_name", disabled=True)
                ed_year = st.text_input("Year became partner", value=csv_p.get("partner_year",""), key="ple_year")
            with d2:
                tiers = _tiers(); t_opts = [""] + tiers if tiers else [""]
                cur_tier = csv_p.get("partner_tier","")
                ed_tier = st.selectbox("Tier", t_opts, index=t_opts.index(cur_tier) if cur_tier in t_opts else 0, key="ple_tier")
                ed_city = st.text_input("City", value=csv_p.get("partner_city",""), key="ple_city")
            with d3:
                cur_country = csv_p.get("partner_country","")
                ed_country = st.selectbox("Country", COUNTRIES, index=COUNTRIES.index(cur_country) if cur_country in COUNTRIES else 0, key="ple_country")
                ed_pam = st.text_input("PAM name", value=csv_p.get("pam_name",""), key="ple_pam")
            ed_pam_email = st.text_input("PAM email", value=csv_p.get("pam_email",""), key="ple_pam_email")

            # Metric scores
            st.markdown('<div class="sec-head">📊 Metric Scores (0 = not scored, 1–5 = score)</div>', unsafe_allow_html=True)
            edit_scores = {}
            for cat in CATEGORIES:
                cat_metrics = [m for m in em if m["key"] in cat["keys"]]
                if not cat_metrics: continue
                st.markdown(f"**{cat['icon']} {cat['label']}**")
                cols = st.columns(min(len(cat_metrics), 3))
                for mi, m in enumerate(cat_metrics):
                    mk = m["key"]
                    try: cur_score = int(csv_p.get(mk, 0) or 0)
                    except: cur_score = 0
                    with cols[mi % len(cols)]:
                        sc = st.number_input(m["name"], min_value=0, max_value=5, value=cur_score,
                            step=1, key=f"ple_s_{mk}",
                            help=f"{m['explanation']}  •  {'Quantitative' if m['type']=='quantitative' else 'Qualitative'}")
                    edit_scores[mk] = sc

            st.markdown("---")
            _, save_col = st.columns([3, 1])
            with save_col:
                edit_sub = st.form_submit_button("💾  Save Changes", use_container_width=True, type="primary")

        if edit_sub:
            # Build updated raw dict and row dict
            new_raw = {"partner_name": edit_pn, "partner_year": ed_year, "partner_tier": ed_tier,
                       "partner_city": ed_city, "partner_country": ed_country,
                       "pam_name": ed_pam, "pam_email": ed_pam_email}
            new_row = dict(new_raw)  # start with same detail fields
            si = {}
            for m in em:
                mk = m["key"]; sc = edit_scores.get(mk, 0)
                if sc and 1 <= sc <= 5:
                    # Generate a synthetic raw value so _rescore_all works
                    new_raw[f"raw_{mk}"] = _synthetic_raw_for_score(mk, sc, cr)
                    new_row[mk] = sc; si[mk] = sc
                else:
                    new_raw[f"raw_{mk}"] = None
                    new_row[mk] = ""
            total = sum(si.values()); sn = len(si); mp = sn * 5
            new_row["total_score"] = total; new_row["max_possible"] = mp
            new_row["percentage"] = round(total / mp * 100, 1) if mp else 0
            _upsert_partner(new_row, new_raw)
            st.session_state["_pl_edit_saved"] = True; st.rerun()

    else:
        # ── Partner table view ──
        if st.session_state.get("_pl_added"):
            st.markdown('<div class="toast">✅ New partner created</div>', unsafe_allow_html=True)
            st.session_state["_pl_added"] = False

        if not partners:
            st.info("No partners yet. Use **Import Data** to bulk-import or add one manually below.")
        else:
            # Build display dataframe
            tbl_data = []
            for p in sorted(partners, key=lambda x: -int(x.get("total_score", 0) or 0)):
                try: pct = float(p.get("percentage", 0) or 0)
                except: pct = 0
                gl, gc = _grade(pct)
                try: ts = int(p.get("total_score", 0) or 0)
                except: ts = 0
                tbl_data.append({
                    "Partner": p.get("partner_name",""),
                    "Tier": p.get("partner_tier",""),
                    "PAM": p.get("pam_name",""),
                    "City": p.get("partner_city",""),
                    "Total Score": ts,
                    "Percentage": f"{pct:.1f}%",
                    "Grade": gl,
                })

            st.dataframe(pd.DataFrame(tbl_data), use_container_width=True, hide_index=True,
                column_config={
                    "Partner": st.column_config.TextColumn(width="large"),
                    "Total Score": st.column_config.NumberColumn(format="%d"),
                })

            # Edit / Delete controls
            st.markdown("---")
            st.markdown("### ✏️ Edit or Delete a Partner")
            partner_names = sorted([p.get("partner_name","") for p in partners])
            sel_partner = st.selectbox("Select partner", partner_names, key="pl_sel_partner")
            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("✏️  Edit Scorecard", use_container_width=True, type="primary", key="pl_edit_btn"):
                    st.session_state["_pl_edit"] = sel_partner; st.rerun()
            with ec2:
                if st.button("🗑️  Delete Partner", use_container_width=True, key="pl_del_btn"):
                    _delete_partner(sel_partner); st.rerun()

        # ── Manual add ──
        st.markdown("---")
        st.markdown("### ➕ Add New Partner")
        with st.form("pl_add_form"):
            a1, a2, a3 = st.columns(3)
            with a1:
                new_name = st.text_input("Partner name *", key="pla_name", placeholder="e.g. Acme Corp")
            with a2:
                new_year = st.text_input("Year became partner", key="pla_year", placeholder="e.g. 2022")
            with a3:
                tiers = _tiers(); t_opts = ["Please choose..."] + tiers if tiers else ["Please choose..."]
                new_tier = st.selectbox("Tier", t_opts, key="pla_tier")
            a4, a5, a6 = st.columns(3)
            with a4: new_city = st.text_input("City", key="pla_city")
            with a5:
                new_country = st.selectbox("Country", COUNTRIES, key="pla_country")
            with a6: new_pam = st.text_input("PAM name", key="pla_pam")

            _, add_col = st.columns([3, 1])
            with add_col:
                add_sub = st.form_submit_button("➕  Add Partner", use_container_width=True, type="primary")

        if add_sub:
            if not new_name or not new_name.strip():
                st.error("Partner name is required.")
            elif _partner_exists(new_name):
                st.error(f"A partner named **{new_name}** already exists.")
            elif _max_partners() and _partner_count() >= _max_partners():
                st.error(f"Partner limit reached (**{_max_partners()}**). Contact your admin to increase the limit.")
            else:
                row = {"partner_name": new_name.strip(), "partner_year": new_year,
                       "partner_tier": new_tier if new_tier != "Please choose..." else "",
                       "partner_city": new_city, "partner_country": new_country,
                       "pam_name": new_pam, "pam_email": "",
                       "total_score": 0, "max_possible": 0, "percentage": 0}
                for m in em: row[m["key"]] = ""
                raw = {"partner_name": new_name.strip(), "partner_year": new_year,
                       "partner_tier": new_tier if new_tier != "Please choose..." else "",
                       "partner_city": new_city, "partner_country": new_country,
                       "pam_name": new_pam, "pam_email": ""}
                _append_partner(row, raw)
                st.session_state["_pl_added"] = True; st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# ASK CHANNELPRO — AI-powered natural language data agent
# ═════════════════════════════════════════════════════════════════════════
elif page=="Ask ChannelPRO":
    _brand(); st.markdown("## 🤖 Ask ChannelPRO")
    if not _save_path().exists():
        st.warning("⚠️ Complete **Step 1 — Scoring Criteria** first."); st.stop()
    st.session_state["criteria"] = json.loads(_save_path().read_text())
    cr = st.session_state["criteria"]
    partners = _load_partners()
    if not partners:
        st.warning("⚠️ Score at least one partner in **Step 2** before using the AI assistant."); st.stop()

    st.markdown("""<div class="info-box">
    Ask questions about your partner scorecards in plain English. Examples:<br>
    • <i>"Which partners have MDF utilization below 40%?"</i><br>
    • <i>"Show me partners with both a low close rate and long sales cycle"</i><br>
    • <i>"Compare the top 5 partners by revenue vs their customer satisfaction"</i><br>
    • <i>"Set Partner X's renewal rate score to 4"</i><br>
    Conversations are multi-turn — ask follow-up questions to refine results.</div>""", unsafe_allow_html=True)

    # API key management
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 Enter your Anthropic API key", type="password", key="ai_api_key",
            help="Set ANTHROPIC_API_KEY environment variable on Render, or enter it here for this session.")
    if not api_key:
        st.info("An Anthropic API key is required. Set `ANTHROPIC_API_KEY` in your Render environment variables, or paste one above.")
        st.stop()

    # Init chat history
    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = []
    if "ai_pending_updates" not in st.session_state:
        st.session_state["ai_pending_updates"] = None

    # ── Pending updates confirmation ──
    if st.session_state["ai_pending_updates"]:
        updates = st.session_state["ai_pending_updates"]
        st.markdown("### ⚠️ Confirm Score Updates")
        st.markdown("The AI has suggested the following changes:")
        upd_rows = ""
        for u in updates:
            upd_rows += f'<tr><td style="text-align:left;padding-left:10px">{u["partner"]}</td>'
            mk = u["metric_key"]
            mname = next((m["name"] for m in SCORECARD_METRICS if m["key"] == mk), mk)
            upd_rows += f'<td>{mname}</td><td style="font-weight:800">{u["new_score"]}/5</td>'
            upd_rows += f'<td style="text-align:left">{u.get("reason","")}</td></tr>'
        st.markdown(f'<table class="hm-tbl"><thead><tr><th style="text-align:left">Partner</th><th>Metric</th><th>New Score</th><th style="text-align:left">Reason</th></tr></thead><tbody>{upd_rows}</tbody></table>', unsafe_allow_html=True)
        uc1, uc2, uc3 = st.columns([1, 1, 3])
        with uc1:
            if st.button("✅ Apply Updates", type="primary", key="ai_confirm_upd"):
                applied = _apply_ai_updates(updates, cr)
                st.session_state["ai_pending_updates"] = None
                st.session_state["ai_messages"].append({"role": "assistant", "content":
                    json.dumps({"answer": f"✅ Applied {applied} score update(s) successfully.", "table": None, "chart": None, "updates": None})})
                st.rerun()
        with uc2:
            if st.button("❌ Cancel", key="ai_cancel_upd"):
                st.session_state["ai_pending_updates"] = None
                st.session_state["ai_messages"].append({"role": "assistant", "content":
                    json.dumps({"answer": "Updates cancelled. No changes were made.", "table": None, "chart": None, "updates": None})})
                st.rerun()
        st.markdown("---")

    # ── Chat history display ──
    for msg in st.session_state["ai_messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                try:
                    resp = json.loads(msg["content"])
                    st.markdown(resp.get("answer","").replace("\\n", "\n"))
                    if resp.get("table"):
                        st.dataframe(pd.DataFrame(resp["table"]), use_container_width=True, hide_index=True)
                    if resp.get("chart"):
                        _render_ai_chart(resp["chart"])
                except:
                    st.markdown(msg["content"])

    # ── Controls row ──
    ctrl1, ctrl2 = st.columns([1, 6])
    with ctrl1:
        if st.button("🗑️ Clear chat", key="ai_clear", use_container_width=True):
            st.session_state["ai_messages"] = []
            st.session_state["ai_pending_updates"] = None
            st.rerun()

    # ── Chat input ──
    user_input = st.chat_input("Ask about your partners...", key="ai_chat_input")
    if user_input:
        # Add user message
        st.session_state["ai_messages"].append({"role": "user", "content": user_input})

        # Build messages for API (only role + content for API call)
        api_messages = []
        for msg in st.session_state["ai_messages"]:
            if msg["role"] == "user":
                api_messages.append({"role": "user", "content": msg["content"]})
            else:
                # Send back the raw JSON as assistant response for context
                api_messages.append({"role": "assistant", "content": msg["content"]})

        # Call API
        with st.spinner("🤖 Analyzing your partner data..."):
            resp = _call_ai(api_messages, api_key)

        # Store response
        resp_json = json.dumps(resp)
        st.session_state["ai_messages"].append({"role": "assistant", "content": resp_json})

        # Handle updates — stage for confirmation
        if resp.get("updates") and isinstance(resp["updates"], list) and len(resp["updates"]) > 0:
            st.session_state["ai_pending_updates"] = resp["updates"]

        st.rerun()


# ═════════════════════════════════════════════════════════════════════════
# ADMIN — MANAGE USERS
# ═════════════════════════════════════════════════════════════════════════
elif page=="Admin — Manage Users":
    _brand(); st.markdown("## Admin — Manage Users & Clients")
    if not is_admin: st.error("Admin access required."); st.stop()
    users=_load_users()
    if st.session_state.get("_admin_saved"):
        st.markdown('<div class="toast">✅ Changes saved</div>',unsafe_allow_html=True); st.session_state["_admin_saved"]=False
    st.markdown("### Current Users")
    for uname,udata in users.items():
        with st.expander(f"{'🔑' if udata['role']=='admin' else '👤'} **{uname}** — {udata['display_name']} ({udata['role']}) {('→ '+udata['tenant']) if udata.get('tenant') else ''}"):
            if uname=="admin": st.caption("Default admin account. You can change the password below.")
            new_pw=st.text_input(f"New password for {uname}",type="password",key=f"adm_pw_{uname}")
            if st.button(f"Update password",key=f"adm_pwbtn_{uname}"):
                if new_pw and len(new_pw)>=4:
                    users[uname]["password_hash"]=_hash_pw(new_pw); _save_users(users)
                    st.session_state["_admin_saved"]=True; st.rerun()
                else: st.error("Password must be at least 4 characters.")
            if uname!="admin":
                if st.button(f"🗑️ Delete user {uname}",key=f"adm_del_{uname}"):
                    del users[uname]; _save_users(users)
                    st.session_state["_admin_saved"]=True; st.rerun()
    st.markdown("---")
    st.markdown("### Add New Client User")
    st.markdown("Each client user gets a **tenant ID** (e.g. `acme_corp`). This isolates their data completely.")
    with st.form("add_user_form"):
        c1,c2=st.columns(2)
        with c1:
            new_uname=st.text_input("Username",placeholder="e.g. acme_user")
            new_display=st.text_input("Display name",placeholder="e.g. Acme Corporation")
        with c2:
            new_password=st.text_input("Password",type="password",placeholder="Min 4 characters")
            new_tenant=st.text_input("Tenant ID",placeholder="e.g. acme_corp (lowercase, no spaces)")
        new_role=st.radio("Role",["client","admin"],horizontal=True)
        add_sub=st.form_submit_button("➕ Add User",type="primary")
    if add_sub:
        errors=[]
        if not new_uname or len(new_uname)<2: errors.append("Username must be at least 2 characters.")
        if new_uname in users: errors.append("Username already exists.")
        if not new_password or len(new_password)<4: errors.append("Password must be at least 4 characters.")
        if new_role=="client" and (not new_tenant or " " in new_tenant): errors.append("Tenant ID is required for client users (no spaces).")
        if new_uname and not re.match(r'^[a-zA-Z0-9_]+$', new_uname): errors.append("Username: letters, numbers, underscores only.")
        if errors:
            for e in errors: st.error(e)
        else:
            tid=new_tenant.lower().strip() if new_tenant else None
            users[new_uname]={"password_hash":_hash_pw(new_password),"display_name":new_display or new_uname,"role":new_role,"tenant":tid if new_role=="client" else None}
            _save_users(users)
            if tid: _tenant_dir(tid)
            st.session_state["_admin_saved"]=True; st.rerun()
    st.markdown("---")
    st.markdown("### Tenant Directories & Limits")
    tenants=_all_tenants()
    if tenants:
        for t in tenants:
            td=_tenant_dir(t)
            has_criteria=(td/"scoring_criteria.json").exists()
            has_partners=(td/"all_partners.csv").exists()
            pc=len(_load_partners(td/"all_partners.csv")) if has_partners else 0
            tcfg = _load_tenant_config(t)
            mp = tcfg.get("max_partners", 0)
            limit_str = f"**{mp}**" if mp else "Unlimited"
            with st.expander(f"**{t}** — {'✅ Criteria' if has_criteria else '⚪ No criteria'} · {pc} partners · Limit: {limit_str}"):
                new_max = st.number_input(
                    f"Max partners for **{t}** (0 = unlimited)",
                    min_value=0, max_value=10000, value=mp, step=5, key=f"adm_maxp_{t}",
                    help="Set the maximum number of partners this client can score. 0 means unlimited.")
                if st.button(f"💾 Save limit for {t}", key=f"adm_maxp_btn_{t}"):
                    tcfg["max_partners"] = new_max
                    _save_tenant_config(tcfg, t)
                    st.session_state["_admin_saved"] = True; st.rerun()
    else:
        st.info("No tenant directories yet. Add a client user above to create one.")

# ═════════════════════════════════════════════════════════════════════════
# ADMIN — ALL CLIENTS OVERVIEW
# ═════════════════════════════════════════════════════════════════════════
elif page=="Admin — All Clients":
    _brand(); st.markdown("## Admin — All Clients Overview")
    if not is_admin: st.error("Admin access required."); st.stop()
    tenants=_all_tenants()
    if not tenants: st.info("No clients yet. Create accounts in **Manage Users**."); st.stop()
    total_partners=0; tenant_data={}
    for t in tenants:
        td=_tenant_dir(t)
        ci=json.loads((td/"client_info.json").read_text()) if (td/"client_info.json").exists() else {}
        ps=_load_partners(td/"all_partners.csv")
        total_partners+=len(ps)
        # Load break-even data if available
        be_file = td / "break_even_configs.json"
        be_data = json.loads(be_file.read_text()) if be_file.exists() else None
        be_total = sum(sum(v for v in items.values()) for items in be_data.get("sections", {}).values()) if be_data else 0
        be_np = be_data.get("num_partners", 0) if be_data else 0
        tenant_data[t]={"client_info":ci,"partners":ps,"has_criteria":(td/"scoring_criteria.json").exists(),
                        "be_data":be_data,"be_total":be_total,"be_np":be_np}
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f'<div class="sum-card"><div class="sum-big">{len(tenants)}</div><div class="sum-lbl">Clients</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sum-card"><div class="sum-big">{total_partners}</div><div class="sum-lbl">Total Partners</div></div>',unsafe_allow_html=True)
    with c3:
        wc=sum(1 for d in tenant_data.values() if d["has_criteria"])
        st.markdown(f'<div class="sum-card"><div class="sum-big">{wc}/{len(tenants)}</div><div class="sum-lbl">Criteria Set</div></div>',unsafe_allow_html=True)
    # Break-even overview row
    be_clients = sum(1 for d in tenant_data.values() if d["be_data"])
    if be_clients > 0:
        total_be = sum(d["be_total"] for d in tenant_data.values())
        b1, b2, b3 = st.columns(3)
        with b1: st.metric("Clients w/ Break-even", f"{be_clients}/{len(tenants)}")
        with b2: st.metric("Total Program Costs (all)", f"${total_be:,.0f}")
        avg_be = total_be / sum(d["be_np"] for d in tenant_data.values() if d["be_np"] > 0) if any(d["be_np"] > 0 for d in tenant_data.values()) else 0
        with b3: st.metric("Avg Break-even/Partner", f"${avg_be:,.2f}")
    st.markdown("---")
    for t in tenants:
        td=tenant_data[t]; ci=td["client_info"]; ps=td["partners"]
        client_name=ci.get("client_name",t)
        with st.expander(f"🏢 **{client_name}** ({t}) — {len(ps)} partners {'✅' if td['has_criteria'] else '⚪'}"):
            if ci:
                c1,c2,c3=st.columns(3)
                with c1: st.markdown(f"**Contact:** {ci.get('project_manager','—')}")
                with c2: st.markdown(f"**Email:** {ci.get('email','—')}")
                with c3: st.markdown(f"**City:** {ci.get('city','—')}, {ci.get('country','—')}")
            if ps:
                sorted_ps=sorted(ps,key=lambda p:-int(p.get("total_score",0) or 0))
                tbl="<table class='hm-tbl'><thead><tr><th>Partner</th><th>PAM</th><th>Total</th><th>%</th><th>Grade</th></tr></thead><tbody>"
                for p in sorted_ps:
                    try: tv=int(p.get("total_score",0) or 0)
                    except: tv=0
                    try: pv=float(p.get("percentage",0) or 0)
                    except: pv=0
                    gl,gc=_grade(pv)
                    tbl+=f'<tr><td style="text-align:left;padding-left:10px">{p.get("partner_name","")}</td><td>{p.get("pam_name","")}</td><td>{tv}</td><td>{pv:.1f}%</td><td style="color:{gc};font-weight:800">{gl}</td></tr>'
                tbl+="</tbody></table>"
                st.markdown(tbl,unsafe_allow_html=True)
                csv_path=_tenant_dir(t)/"all_partners.csv"
                if csv_path.exists(): st.download_button(f"⬇️ Download {t} CSV",csv_path.read_text(),f"{t}_partners.csv","text/csv",key=f"dl_{t}")
            else: st.caption("No partners scored yet.")
            # Break-even summary
            if td.get("be_data"):
                st.markdown("---")
                bc1, bc2, bc3 = st.columns(3)
                with bc1: st.metric("Program Costs", f"${td['be_total']:,.0f}")
                be_pt = td['be_total'] / td['be_np'] if td['be_np'] > 0 else 0
                with bc2: st.metric("Break-even/Partner", f"${be_pt:,.2f}")
                sup_t = sum(td["be_data"].get("sections",{}).get("Technical and Sales Support",{}).values())
                with bc3: st.metric("Support Costs", f"${sup_t:,.0f}")
    st.markdown("---"); st.markdown("### Cross-Client Export")
    if st.button("⬇️  Export All Clients to Single Excel",type="primary"):
        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
            wb=openpyxl.Workbook(); first=True
            for t in tenants:
                td_info=tenant_data[t]; ps=td_info["partners"]
                if not ps: continue
                cn=td_info["client_info"].get("client_name",t)[:31]
                if first: ws=wb.active; ws.title=cn; first=False
                else: ws=wb.create_sheet(title=cn)
                hf=PatternFill(start_color="1E2A3A",end_color="1E2A3A",fill_type="solid")
                hfont=Font(color="FFFFFF",bold=True,size=10)
                bdr=Border(left=Side(style="thin",color="CCCCCC"),right=Side(style="thin",color="CCCCCC"),top=Side(style="thin",color="CCCCCC"),bottom=Side(style="thin",color="CCCCCC"))
                headers=["Partner","PAM","Total Score","Percentage","Grade"]
                for ci_idx,h in enumerate(headers,1):
                    c=ws.cell(1,ci_idx,h); c.fill=hf; c.font=hfont; c.border=bdr; c.alignment=Alignment(horizontal="center")
                ws.column_dimensions["A"].width=28; ws.column_dimensions["B"].width=22
                sorted_ps=sorted(ps,key=lambda p:-int(p.get("total_score",0) or 0))
                for ri,p in enumerate(sorted_ps,2):
                    try: tv=int(p.get("total_score",0) or 0)
                    except: tv=0
                    try: pv=float(p.get("percentage",0) or 0)
                    except: pv=0
                    gl,_=_grade(pv)
                    ws.cell(ri,1,p.get("partner_name","")).border=bdr
                    ws.cell(ri,2,p.get("pam_name","")).border=bdr
                    ws.cell(ri,3,tv).border=bdr; ws.cell(ri,3).alignment=Alignment(horizontal="center")
                    pc=ws.cell(ri,4); pc.value=pv/100; pc.number_format="0.0%"; pc.border=bdr; pc.alignment=Alignment(horizontal="center")
                    ws.cell(ri,5,gl).border=bdr; ws.cell(ri,5).alignment=Alignment(horizontal="center")
            buf=io.BytesIO(); wb.save(buf)
            st.download_button("📥 Download",buf.getvalue(),"All_Clients_Overview.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except ImportError: st.warning("Install openpyxl for Excel export.")


# ═════════════════════════════════════════════════════════════════════════
# BREAK-EVEN — PROGRAM COSTS
# ═════════════════════════════════════════════════════════════════════════
elif page=="Break-even — Program Costs":
    _brand(); st.markdown("## Break-even — Program Costs")
    st.markdown("""<div class="info-box">
    Enter your annual partner program costs by category. The tool calculates your <b>total program cost</b>
    and <b>nominal break-even point</b> (cost per partner). For <b>Technical and Sales Support</b>, it also
    derives cost-per-call and cost-per-minute metrics used in the Detailed Analysis page.</div>""", unsafe_allow_html=True)

    cfg = _load_be()
    if st.session_state.get("_be_saved"):
        st.markdown('<div class="toast">✅ Break-even configuration saved</div>', unsafe_allow_html=True)
        st.session_state["_be_saved"] = False

    # Custom categories in session state
    if "be_custom" not in st.session_state:
        st.session_state["be_custom"] = cfg.get("custom_items", {})

    # --- Add custom category UI (outside form) ---
    with st.expander("➕ Add custom cost category"):
        ac1, ac2 = st.columns(2)
        sec_names = [s["section"] for s in BE_SECTIONS] + ["— New section —"]
        with ac1: add_sec = st.selectbox("Section", sec_names, key="be_add_sec")
        with ac2:
            new_sec_name = ""
            if add_sec == "— New section —":
                new_sec_name = st.text_input("New section name", key="be_new_sec")
            add_item = st.text_input("Cost category name", key="be_add_item")
        if st.button("➕ Add", key="be_add_btn"):
            target = new_sec_name.strip() if add_sec == "— New section —" else add_sec
            if target and add_item.strip():
                custom = st.session_state["be_custom"]
                if target not in custom: custom[target] = {}
                custom[target][add_item.strip()] = 0
                st.rerun()

    # --- Main cost form ---
    with st.form("be_form"):
        new_cfg = {"sections": {}, "custom_items": st.session_state.get("be_custom", {})}

        grand_total = 0
        support_subtotal = 0

        # Iterate default sections + custom-only sections
        all_sec_names = [s["section"] for s in BE_SECTIONS]
        custom = st.session_state.get("be_custom", {})
        for csk in custom:
            if csk not in all_sec_names: all_sec_names.append(csk)

        for sec_name in all_sec_names:
            # Find default items
            default_sec = next((s for s in BE_SECTIONS if s["section"] == sec_name), None)
            default_items = default_sec["items"] if default_sec else []
            custom_items = list(custom.get(sec_name, {}).keys())
            all_items = default_items + [ci for ci in custom_items if ci not in default_items]

            if not all_items: continue

            icon = BE_SECTION_ICONS.get(sec_name, "📁")
            st.markdown(f'<div class="sec-head">{icon} {sec_name}</div>', unsafe_allow_html=True)

            sec_data = {}; sec_total = 0
            saved_sec = cfg.get("sections", {}).get(sec_name, {})
            # Layout: 2 columns of items
            cols = st.columns(2)
            for idx, item in enumerate(all_items):
                saved_val = saved_sec.get(item, custom.get(sec_name, {}).get(item, 0))
                with cols[idx % 2]:
                    v = st.number_input(item, min_value=0, value=int(saved_val or 0),
                                        step=500, key=f"be_{sec_name}_{item}", format="%d")
                sec_data[item] = v; sec_total += v

            st.markdown(f"**Sub-total: ${sec_total:,.0f}**")
            new_cfg["sections"][sec_name] = sec_data
            grand_total += sec_total
            if sec_name == "Technical and Sales Support":
                support_subtotal = sec_total

        # --- Global inputs ---
        st.markdown('<div class="sec-head">🔢 Program Parameters</div>', unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns(3)
        existing_partners = len(_load_partners())
        with pc1:
            num_p = st.number_input("Number of partners", min_value=1,
                value=int(cfg.get("num_partners") or existing_partners or 60), step=1, key="be_num_partners")
        with pc2:
            sup_calls = st.number_input("# of support calls (annual)", min_value=0,
                value=int(cfg.get("support_calls", 0)), step=100, key="be_sup_calls")
        with pc3:
            avg_min = st.number_input("Avg minutes per call", min_value=1,
                value=int(cfg.get("avg_min_per_call", 20)), step=1, key="be_avg_min")

        new_cfg["num_partners"] = num_p
        new_cfg["support_calls"] = sup_calls
        new_cfg["avg_min_per_call"] = avg_min

        st.markdown("---")
        _, bc = st.columns([3, 1])
        with bc: be_sub = st.form_submit_button("💾 Save Configuration", use_container_width=True, type="primary")

    if be_sub:
        _save_be(new_cfg); cfg = new_cfg
        st.session_state["_be_saved"] = True; st.rerun()

    # --- Results dashboard ---
    st.markdown("---")
    st.markdown("### 📊 Program Cost Summary")

    # Recalculate from cfg
    gt = sum(sum(v for v in items.values()) for items in cfg.get("sections", {}).values())
    np_ = cfg.get("num_partners", 1) or 1
    be_point = gt / np_
    sc_ = cfg.get("support_calls", 0) or 0
    am_ = cfg.get("avg_min_per_call", 20) or 20
    sup_cost = sum(cfg.get("sections", {}).get("Technical and Sales Support", {}).values())
    cpc = sup_cost / sc_ if sc_ > 0 else 0
    cpm = sup_cost / (sc_ * am_) if sc_ > 0 and am_ > 0 else 0

    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="sum-card"><div class="sum-big">${gt:,.0f}</div><div class="sum-lbl">Total Program Costs</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="sum-card"><div class="sum-big">{np_}</div><div class="sum-lbl">Number of Partners</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="sum-card"><div class="sum-big" style="color:#49a34f">${be_point:,.2f}</div><div class="sum-lbl">Break-even per Partner</div></div>', unsafe_allow_html=True)

    if sup_cost > 0:
        st.markdown("#### 🛠️ Support Cost Metrics")
        s1, s2, s3, s4 = st.columns(4)
        with s1: st.metric("Support Costs", f"${sup_cost:,.0f}")
        with s2: st.metric("# Support Calls", f"{sc_:,}")
        with s3: st.metric("Cost per Call", f"${cpc:,.2f}")
        with s4: st.metric("Cost per Minute", f"${cpm:,.4f}")

    # Section breakdown table
    st.markdown("#### Cost Breakdown by Section")
    breakdown_rows = ""
    cfg_sections = list(cfg.get("sections", {}).keys())
    if not cfg_sections:
        cfg_sections = [s["section"] for s in BE_SECTIONS]
    for sec_name in cfg_sections:
        sec_items = cfg.get("sections", {}).get(sec_name, {})
        sec_t = sum(sec_items.values())
        pct = (sec_t / gt * 100) if gt > 0 else 0
        icon = BE_SECTION_ICONS.get(sec_name, "📁")
        breakdown_rows += f'<tr><td style="text-align:left;padding-left:10px">{icon} {sec_name}</td><td>${sec_t:,.0f}</td><td>{pct:.1f}%</td></tr>'
    if gt > 0:
        breakdown_rows += f'<tr class="hm-total"><td style="text-align:left;padding-left:10px;font-weight:800">TOTAL</td><td style="font-weight:800">${gt:,.0f}</td><td style="font-weight:800">100%</td></tr>'
    st.markdown(f'<table class="hm-tbl"><thead><tr><th style="text-align:left">Section</th><th>Cost</th><th>% of Total</th></tr></thead><tbody>{breakdown_rows}</tbody></table>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════
# BREAK-EVEN — DETAILED ANALYSIS
# ═════════════════════════════════════════════════════════════════════════
elif page=="Break-even — Detailed Analysis":
    _brand(); st.markdown("## Break-even — Detailed Partner Cost Analysis")

    # Load break-even config for cost metrics
    be_cfg = _load_be()
    sup_cost = sum(be_cfg.get("sections", {}).get("Technical and Sales Support", {}).values())
    sc_ = be_cfg.get("support_calls", 0) or 0
    am_ = be_cfg.get("avg_min_per_call", 20) or 20
    cpm = sup_cost / (sc_ * am_) if sc_ > 0 and am_ > 0 else 0
    cpc = sup_cost / sc_ if sc_ > 0 else 0

    if sup_cost == 0:
        st.warning("⚠️ Complete **Break-even — Program Costs** first to set support cost metrics.")

    st.markdown("""<div class="info-box">
    Upload a CSV with columns: <b>Partner</b>, <b>Revenues</b>, <b># of calls</b>.
    Optional: <b>Time spent</b> (minutes). If missing, it will be estimated using your configured average minutes per call.
    Support cost per partner is calculated using cost-per-minute from your Program Costs configuration.</div>""", unsafe_allow_html=True)

    # Show current cost metrics
    cm1, cm2, cm3 = st.columns(3)
    with cm1: st.metric("Cost per Minute", f"${cpm:,.4f}" if cpm > 0 else "Not set")
    with cm2: st.metric("Cost per Call", f"${cpc:,.2f}" if cpc > 0 else "Not set")
    with cm3: st.metric("Avg Min/Call", f"{am_}")

    st.markdown("---")

    # Configurable avg minutes per call for this analysis
    avg_min_override = st.number_input("Average minutes per call (for estimating missing 'Time spent')",
        min_value=1, value=am_, step=1, key="da_avg_min")

    # File upload
    uploaded = st.file_uploader("📁 Upload Partner Cost CSV", type=["csv"], key="da_upload")

    # Try loading previously saved data
    df = None
    sd_path = _sd_path()

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Error reading CSV: {e}"); df = None
    elif sd_path.exists():
        try:
            df = pd.read_csv(sd_path)
            st.info("📂 Loaded previously saved analysis data.")
        except: df = None

    if df is None:
        st.info("Upload a CSV to begin analysis, or complete one on the Program Costs page first.")
        st.stop()

    # Validate required columns
    col_map = {}
    for col in df.columns:
        cl = col.strip().lower()
        if cl in ("partner", "partner name"): col_map["Partner"] = col
        elif cl in ("revenues", "revenue"): col_map["Revenues"] = col
        elif cl in ("# of calls", "calls", "number of calls", "#calls"): col_map["Calls"] = col
        elif cl in ("time spent", "time", "minutes", "time spent (min)"): col_map["Time"] = col

    missing = [c for c in ["Partner", "Revenues", "Calls"] if c not in col_map]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}. Found: {list(df.columns)}")
        st.stop()

    # Normalize column names
    df = df.rename(columns={col_map["Partner"]: "Partner", col_map["Revenues"]: "Revenues", col_map["Calls"]: "# of calls"})
    if "Time" in col_map:
        df = df.rename(columns={col_map["Time"]: "Time spent"})

    # Clean numeric columns
    for c in ["Revenues", "# of calls"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    if "Time spent" in df.columns:
        df["Time spent"] = pd.to_numeric(df["Time spent"], errors="coerce").fillna(0)
    else:
        df["Time spent"] = df["# of calls"] * avg_min_override

    # Fill missing time using avg
    df.loc[df["Time spent"] == 0, "Time spent"] = df.loc[df["Time spent"] == 0, "# of calls"] * avg_min_override

    # Sort by revenues descending
    df = df.sort_values("Revenues", ascending=False).reset_index(drop=True)

    # Calculate percentages and costs
    total_rev = df["Revenues"].sum()
    total_calls = df["# of calls"].sum()
    total_time = df["Time spent"].sum()

    df["% of revenues"] = (df["Revenues"] / total_rev * 100) if total_rev > 0 else 0
    df["% of calls"] = (df["# of calls"] / total_calls * 100) if total_calls > 0 else 0
    df["% of support time"] = (df["Time spent"] / total_time * 100) if total_time > 0 else 0

    if cpm > 0:
        df["Support cost"] = df["Time spent"] * cpm
    elif cpc > 0:
        df["Support cost"] = df["# of calls"] * cpc
    else:
        df["Support cost"] = 0

    total_support_cost = df["Support cost"].sum()
    df["% of cost"] = (df["Support cost"] / total_support_cost * 100) if total_support_cost > 0 else 0

    # Save processed data
    df.to_csv(sd_path, index=False)

    # --- Display results ---
    st.markdown("### 📊 Analysis Results")
    rm1, rm2, rm3, rm4 = st.columns(4)
    with rm1: st.metric("Partners", f"{len(df)}")
    with rm2: st.metric("Total Revenue", f"${total_rev:,.0f}")
    with rm3: st.metric("Total Calls", f"{int(total_calls):,}")
    with rm4: st.metric("Total Support Cost", f"${total_support_cost:,.2f}")

    # Display table
    st.markdown("### Partner Cost Table")
    display_df = df[["Partner", "Revenues", "% of revenues", "# of calls", "% of calls",
                     "Time spent", "% of support time", "Support cost", "% of cost"]].copy()

    # Add totals row
    totals = pd.DataFrame([{
        "Partner": "TOTAL", "Revenues": total_rev,
        "% of revenues": 100.0, "# of calls": total_calls,
        "% of calls": 100.0, "Time spent": total_time,
        "% of support time": 100.0, "Support cost": total_support_cost,
        "% of cost": 100.0
    }])
    display_with_totals = pd.concat([display_df, totals], ignore_index=True)

    # Format for display
    fmt_df = display_with_totals.copy()
    fmt_df["Revenues"] = fmt_df["Revenues"].apply(lambda x: f"${x:,.0f}")
    fmt_df["% of revenues"] = fmt_df["% of revenues"].apply(lambda x: f"{x:.1f}%")
    fmt_df["# of calls"] = fmt_df["# of calls"].apply(lambda x: f"{int(x):,}")
    fmt_df["% of calls"] = fmt_df["% of calls"].apply(lambda x: f"{x:.1f}%")
    fmt_df["Time spent"] = fmt_df["Time spent"].apply(lambda x: f"{int(x):,}")
    fmt_df["% of support time"] = fmt_df["% of support time"].apply(lambda x: f"{x:.1f}%")
    fmt_df["Support cost"] = fmt_df["Support cost"].apply(lambda x: f"${x:,.2f}")
    fmt_df["% of cost"] = fmt_df["% of cost"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(fmt_df, use_container_width=True, hide_index=True)

    # Downloads
    dl1, dl2 = st.columns(2)
    with dl1:
        csv_buf = display_with_totals.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv_buf, "partner_cost_analysis.csv", "text/csv", type="primary")
    with dl2:
        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Partner Costs"
            hf = PatternFill(start_color="1E2A3A", end_color="1E2A3A", fill_type="solid")
            hfont = Font(color="FFFFFF", bold=True, size=10)
            bdr = Border(left=Side(style="thin", color="CCCCCC"), right=Side(style="thin", color="CCCCCC"),
                         top=Side(style="thin", color="CCCCCC"), bottom=Side(style="thin", color="CCCCCC"))
            headers = list(display_with_totals.columns)
            for ci, h in enumerate(headers, 1):
                c = ws.cell(1, ci, h); c.fill = hf; c.font = hfont; c.border = bdr
                c.alignment = Alignment(horizontal="center", wrap_text=True)
                ws.column_dimensions[c.column_letter].width = 16
            ws.column_dimensions["A"].width = 24
            for ri, (_, row) in enumerate(display_with_totals.iterrows(), 2):
                for ci, h in enumerate(headers, 1):
                    v = row[h]
                    cell = ws.cell(ri, ci, v); cell.border = bdr
                    cell.alignment = Alignment(horizontal="center")
                    if h in ("Revenues", "Support cost") and isinstance(v, (int, float)):
                        cell.number_format = '#,##0'
                    elif "%" in h and isinstance(v, (int, float)):
                        cell.value = v / 100; cell.number_format = "0.0%"
                    if row["Partner"] == "TOTAL":
                        cell.font = Font(bold=True)
            buf = io.BytesIO(); wb.save(buf)
            st.download_button("⬇️ Download Excel", buf.getvalue(), "partner_cost_analysis.xlsx",
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except ImportError: pass

    # --- Visualizations ---
    st.markdown("---")
    st.markdown("### 📈 Visualizations")

    chart_df = df.head(15).copy()
    if len(chart_df) > 0 and total_support_cost > 0:
        import altair as alt

        tab1, tab2, tab3 = st.tabs(["Support Cost vs Revenue", "Cost Distribution", "Cost/Revenue Ratio"])

        with tab1:
            st.markdown("#### Top Partners: Support Cost vs Revenue")
            # Melt for grouped bar chart
            bar_src = chart_df[["Partner", "Revenues", "Support cost"]].copy()
            bar_src = bar_src.melt(id_vars="Partner", var_name="Metric", value_name="Amount")
            bar_chart = alt.Chart(bar_src).mark_bar().encode(
                x=alt.X("Partner:N", sort=list(chart_df["Partner"]), axis=alt.Axis(labelAngle=-45, labelLimit=120)),
                y=alt.Y("Amount:Q", title="$"),
                color=alt.Color("Metric:N", scale=alt.Scale(domain=["Revenues","Support cost"], range=["#2563eb","#dc4040"])),
                xOffset="Metric:N",
                tooltip=["Partner", "Metric", alt.Tooltip("Amount:Q", format="$,.0f")]
            ).properties(height=400)
            st.altair_chart(bar_chart, use_container_width=True)

        with tab2:
            st.markdown("#### Cost Distribution by Partner")
            top10 = df.head(10).copy()
            rest_cost = df.iloc[10:]["Support cost"].sum() if len(df) > 10 else 0
            pie_src = top10[["Partner", "Support cost"]].copy()
            if rest_cost > 0:
                pie_src = pd.concat([pie_src, pd.DataFrame([{"Partner": "Others", "Support cost": rest_cost}])], ignore_index=True)
            pie_chart = alt.Chart(pie_src).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("Support cost:Q"),
                color=alt.Color("Partner:N", legend=alt.Legend(title="Partner")),
                tooltip=["Partner", alt.Tooltip("Support cost:Q", format="$,.2f")]
            ).properties(height=400)
            st.altair_chart(pie_chart, use_container_width=True)

            # Revenue distribution pie
            st.markdown("#### Revenue Distribution by Partner")
            rev_src = top10[["Partner", "Revenues"]].copy()
            rest_rev = df.iloc[10:]["Revenues"].sum() if len(df) > 10 else 0
            if rest_rev > 0:
                rev_src = pd.concat([rev_src, pd.DataFrame([{"Partner": "Others", "Revenues": rest_rev}])], ignore_index=True)
            rev_pie = alt.Chart(rev_src).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("Revenues:Q"),
                color=alt.Color("Partner:N", legend=alt.Legend(title="Partner")),
                tooltip=["Partner", alt.Tooltip("Revenues:Q", format="$,.0f")]
            ).properties(height=400)
            st.altair_chart(rev_pie, use_container_width=True)

        with tab3:
            st.markdown("#### Cost / Revenue Ratio by Partner")
            ratio_df = chart_df[["Partner", "Revenues", "# of calls", "Support cost"]].copy()
            ratio_df["Cost/Rev %"] = ratio_df.apply(lambda r: (r["Support cost"] / r["Revenues"] * 100) if r["Revenues"] > 0 else 0, axis=1)
            ratio_chart = alt.Chart(ratio_df).mark_bar().encode(
                x=alt.X("Partner:N", sort=list(chart_df["Partner"]), axis=alt.Axis(labelAngle=-45, labelLimit=120)),
                y=alt.Y("Cost/Rev %:Q", title="Support Cost as % of Revenue"),
                color=alt.condition(
                    alt.datum["Cost/Rev %"] > 10, alt.value("#dc4040"),
                    alt.condition(alt.datum["Cost/Rev %"] > 5, alt.value("#d4a917"), alt.value("#1b6e23"))
                ),
                tooltip=["Partner", alt.Tooltip("Revenues:Q", format="$,.0f"),
                         alt.Tooltip("Support cost:Q", format="$,.2f"),
                         alt.Tooltip("Cost/Rev %:Q", format=".1f")]
            ).properties(height=400)
            st.altair_chart(ratio_chart, use_container_width=True)

            # Table view
            st.markdown("##### Detail")
            tbl_html = '<table class="hm-tbl"><thead><tr><th style="text-align:left">Partner</th><th>Revenue</th><th>Calls</th><th>Support Cost</th><th>Cost/Rev %</th></tr></thead><tbody>'
            for _, r in ratio_df.iterrows():
                rc = "#dc4040" if r["Cost/Rev %"] > 10 else "#d4a917" if r["Cost/Rev %"] > 5 else "#1b6e23"
                tbl_html += f'<tr><td style="text-align:left;padding-left:10px">{r["Partner"]}</td><td>${r["Revenues"]:,.0f}</td><td>{int(r["# of calls"]):,}</td><td>${r["Support cost"]:,.2f}</td><td style="color:{rc};font-weight:700">{r["Cost/Rev %"]:.1f}%</td></tr>'
            tbl_html += '</tbody></table>'
            st.markdown(tbl_html, unsafe_allow_html=True)
    else:
        st.info("Add support cost data in Program Costs and upload partner data to see visualizations.")

