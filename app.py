"""
Partner Scorecard — Phase 1: Define Scoring Criteria
=====================================================
Streamlit app that lets the user configure 1-5 scoring ranges/descriptors
for each of the 28 partner-scorecard metrics extracted from
Partner_Scorecard.xlsx.

Run:  streamlit run app.py
"""

import json
import pathlib
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────
# 0.  METRIC DEFINITIONS  (embedded so the app is fully self-contained)
# ─────────────────────────────────────────────────────────────────────────

SCORECARD_METRICS: list[dict] = [
    {
        "id": 1, "key": "annual_revenues",
        "name": "Annual revenues for vendor",
        "explanation": "Total amount received from the partner, net of discounts/margins. Past 12 months or last fiscal year.",
        "type": "quantitative", "format": "currency_range", "unit": "$", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 50_000}, "2": {"min": 50_001, "max": 150_000},
            "3": {"min": 150_001, "max": 350_000}, "4": {"min": 350_001, "max": 750_000},
            "5": {"min": 750_001, "max": None},
        },
    },
    {
        "id": 2, "key": "yoy_revenue_growth",
        "name": "Year-on-year revenue growth",
        "explanation": "Percentage increase/decrease in revenues, past 12 months over previous 12 months.",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": None, "max": 0}, "2": {"min": 0, "max": 10},
            "3": {"min": 10, "max": 20}, "4": {"min": 20, "max": 35},
            "5": {"min": 35, "max": None},
        },
    },
    {
        "id": 3, "key": "net_new_logo_revenues",
        "name": "Net-new logo revenues",
        "explanation": "Revenues from selling to new customers over the past 12 months or last fiscal year.",
        "type": "quantitative", "format": "currency_range", "unit": "$", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 10_000}, "2": {"min": 10_001, "max": 50_000},
            "3": {"min": 50_001, "max": 150_000}, "4": {"min": 150_001, "max": 350_000},
            "5": {"min": 350_001, "max": None},
        },
    },
    {
        "id": 4, "key": "pct_revenues_saas",
        "name": "Percentage of vendor revenues from SaaS",
        "explanation": "How successful the partner has been in transforming from on-premise to SaaS/recurring revenues.",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 20}, "2": {"min": 20, "max": 40},
            "3": {"min": 40, "max": 60}, "4": {"min": 60, "max": 80},
            "5": {"min": 80, "max": 100},
        },
    },
    {
        "id": 5, "key": "average_deal_size",
        "name": "Average deal size",
        "explanation": "Average annualized subscription/license value. Excludes services, maintenance, or software assurance.",
        "type": "quantitative", "format": "currency_range", "unit": "$", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 5_000}, "2": {"min": 5_001, "max": 15_000},
            "3": {"min": 15_001, "max": 40_000}, "4": {"min": 40_001, "max": 100_000},
            "5": {"min": 100_001, "max": None},
        },
    },
    {
        "id": 6, "key": "avg_time_to_close",
        "name": "Average time to close",
        "explanation": "Time from deal registration to signed subscription/EULA. Excludes payment cycle.",
        "type": "quantitative", "format": "number_range", "unit": "days", "direction": "lower_is_better",
        "default_ranges": {
            "1": {"min": 181, "max": None}, "2": {"min": 121, "max": 180},
            "3": {"min": 61, "max": 120}, "4": {"min": 31, "max": 60},
            "5": {"min": 0, "max": 30},
        },
    },
    {
        "id": 7, "key": "renewal_rate",
        "name": "Renewal rate",
        "explanation": "Percentage of subscriptions renewed during the past 12 months or last fiscal year.",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 60}, "2": {"min": 60, "max": 75},
            "3": {"min": 75, "max": 85}, "4": {"min": 85, "max": 93},
            "5": {"min": 93, "max": 100},
        },
    },
    {
        "id": 8, "key": "net_revenue_expansion",
        "name": "Net revenue expansion",
        "explanation": "Growth in revenues for existing customers (negative churn).",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": None, "max": 0}, "2": {"min": 0, "max": 5},
            "3": {"min": 5, "max": 15}, "4": {"min": 15, "max": 25},
            "5": {"min": 25, "max": None},
        },
    },
    {
        "id": 9, "key": "registered_deals",
        "name": "Registered deals",
        "explanation": "Number of deals partner registered with vendor.",
        "type": "quantitative", "format": "number_range", "unit": "count", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 5}, "2": {"min": 6, "max": 15},
            "3": {"min": 16, "max": 30}, "4": {"min": 31, "max": 60},
            "5": {"min": 61, "max": None},
        },
    },
    {
        "id": 10, "key": "win_loss_ratio",
        "name": "Win/loss ratio for registered deals",
        "explanation": "Percentage of registered deals from partner that closed.",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 10}, "2": {"min": 10, "max": 25},
            "3": {"min": 25, "max": 40}, "4": {"min": 40, "max": 60},
            "5": {"min": 60, "max": 100},
        },
    },
    {
        "id": 11, "key": "partner_generated_opps_pct",
        "name": "Partner Generated Opportunities as a % of Pipeline",
        "explanation": "Opportunities the partner generated vs. leads the vendor sent them.",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 10}, "2": {"min": 10, "max": 25},
            "3": {"min": 25, "max": 50}, "4": {"min": 50, "max": 75},
            "5": {"min": 75, "max": 100},
        },
    },
    {
        "id": 12, "key": "frequency_of_business",
        "name": "Frequency of business",
        "explanation": "How many transactions in a 12-month period — steady flow or seasonal?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Sporadic — 1-2 transactions/year, large gaps",
            "2": "Seasonal — clustered in 1-2 quarters only",
            "3": "Moderate — activity most quarters, some gaps",
            "4": "Consistent — monthly or near-monthly transactions",
            "5": "Highly active — weekly/continuous deal flow year-round",
        },
    },
    {
        "id": 13, "key": "mdf_utilization_rate",
        "name": "MDF utilization rate",
        "explanation": "Are they making use of vendor-sponsored marketing funds?",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 20}, "2": {"min": 20, "max": 40},
            "3": {"min": 40, "max": 60}, "4": {"min": 60, "max": 80},
            "5": {"min": 80, "max": 100},
        },
    },
    {
        "id": 14, "key": "quality_of_sales_org",
        "name": "Quality of sales organization",
        "explanation": "Tied to deal size, time to close, win/loss ratio. Do they need more sales guidance?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Weak — no dedicated sales reps, no pipeline discipline",
            "2": "Below average — reps exist but lack product knowledge",
            "3": "Adequate — competent team, average deal metrics",
            "4": "Strong — skilled reps, good pipeline management",
            "5": "Excellent — top-tier team, consistently high deal metrics",
        },
    },
    {
        "id": 15, "key": "customer_satisfaction",
        "name": "Customer satisfaction",
        "explanation": "Do you or the partner measure customer satisfaction, e.g., NPS score?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "No measurement; frequent complaints / escalations",
            "2": "Anecdotal only; some known dissatisfaction",
            "3": "Measured informally; average satisfaction",
            "4": "Formal NPS/CSAT in place; consistently positive",
            "5": "Industry-leading satisfaction scores; referenceable customers",
        },
    },
    {
        "id": 16, "key": "vendor_certifications",
        "name": "Vendor certification(s)",
        "explanation": "How many certifications do they have? Are they investing in learning your technology?",
        "type": "quantitative", "format": "number_range", "unit": "certs", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 0}, "2": {"min": 1, "max": 2},
            "3": {"min": 3, "max": 5}, "4": {"min": 6, "max": 10},
            "5": {"min": 11, "max": None},
        },
    },
    {
        "id": 17, "key": "sales_support_calls",
        "name": "Sales support calls received",
        "explanation": "Calling because of big pipeline, or because they can't sell your solution?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Excessive calls driven by lack of basic product knowledge",
            "2": "Frequent calls on routine questions they should know",
            "3": "Moderate calls — mix of pipeline-driven and knowledge gaps",
            "4": "Calls mostly deal-strategy-driven; few basic questions",
            "5": "Calls are rare and always tied to complex, high-value deals",
        },
    },
    {
        "id": 18, "key": "tech_support_calls",
        "name": "Tech support calls received",
        "explanation": "Are they calling a lot because they lack proper training and certifications?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Excessive calls; clear training/certification gaps",
            "2": "Frequent calls on issues certifications should cover",
            "3": "Average volume; occasionally escalates routine issues",
            "4": "Low volume; mostly complex edge-case questions",
            "5": "Minimal calls; self-sufficient, resolves most issues in-house",
        },
    },
    {
        "id": 19, "key": "communication_with_vendor",
        "name": "Communication with vendor",
        "explanation": "Quality of communications — regular calls, QBRs, mutual visits.",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Unresponsive — no regular cadence, hard to reach",
            "2": "Reactive only — responds when contacted, no proactive updates",
            "3": "Periodic — monthly calls but no formal QBR",
            "4": "Strong — regular cadence, quarterly QBRs, occasional visits",
            "5": "Exemplary — weekly touchpoints, QBRs, mutual exec visits",
        },
    },
    {
        "id": 20, "key": "total_revenues",
        "name": "Total revenues (if available)",
        "explanation": "Overall revenues for the partner including all products and services.",
        "type": "quantitative", "format": "currency_range", "unit": "$", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 1_000_000}, "2": {"min": 1_000_001, "max": 5_000_000},
            "3": {"min": 5_000_001, "max": 20_000_000}, "4": {"min": 20_000_001, "max": 100_000_000},
            "5": {"min": 100_000_001, "max": None},
        },
    },
    {
        "id": 21, "key": "dedication_vs_competitive",
        "name": "Dedication vs. competitive products",
        "explanation": "Are you the strategic vendor, or do they sell more of a competitor and only sell you by request?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Sells competitor as primary; you are an afterthought",
            "2": "Competitor is default; sells you only when asked",
            "3": "Sells both roughly equally; no clear preference",
            "4": "You are the preferred vendor; competitor is secondary",
            "5": "Exclusively or overwhelmingly sells your solution",
        },
    },
    {
        "id": 22, "key": "dedication_vs_other_vendors",
        "name": "Dedication vs. other vendors",
        "explanation": "What percentage of their overall business does your solution represent (license/subscription + related services)?",
        "type": "quantitative", "format": "percentage_range", "unit": "%", "direction": "higher_is_better",
        "default_ranges": {
            "1": {"min": 0, "max": 5}, "2": {"min": 5, "max": 15},
            "3": {"min": 15, "max": 30}, "4": {"min": 30, "max": 50},
            "5": {"min": 50, "max": 100},
        },
    },
    {
        "id": 23, "key": "geographical_coverage",
        "name": "Geographical market coverage",
        "explanation": "Right-sized territory? Covering too much? Potential to expand?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Very limited local presence; no expansion capacity",
            "2": "Small territory with limited reach; gaps in coverage",
            "3": "Adequate regional coverage; some white-space areas",
            "4": "Strong multi-region presence aligned with vendor targets",
            "5": "National/international coverage or dominant in key markets",
        },
    },
    {
        "id": 24, "key": "vertical_coverage",
        "name": "Vertical market coverage",
        "explanation": "Specialize in certain verticals? Large existing customer base in those verticals?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "No vertical focus; generalist with thin expertise",
            "2": "Emerging in 1 vertical; small customer base",
            "3": "Established in 1-2 verticals; moderate customer base",
            "4": "Strong domain expertise; recognized in target verticals",
            "5": "Dominant vertical authority; deep customer base & thought leadership",
        },
    },
    {
        "id": 25, "key": "quality_of_management",
        "name": "Quality of management",
        "explanation": "Subjective assessment — how well do they run their overall business?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Poor — disorganized, high turnover, unclear strategy",
            "2": "Below average — reactive management, inconsistent execution",
            "3": "Adequate — competent but no stand-out leadership",
            "4": "Strong — proactive, clear strategy, stable team",
            "5": "Exceptional — visionary leadership, strong culture, growing",
        },
    },
    {
        "id": 26, "key": "known_litigation",
        "name": "Known litigation (No=5, Yes=1)",
        "explanation": "Are they involved in any lawsuits?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Active major litigation posing existential/reputational risk",
            "2": "Active litigation with material financial exposure",
            "3": "Minor pending litigation; low-severity disputes",
            "4": "Past litigation fully resolved; no current cases",
            "5": "No known litigation history",
        },
    },
    {
        "id": 27, "key": "export_control_ip",
        "name": "Export control and protection of intellectual property",
        "explanation": "Are they complying with export control and IP provisions in the partner agreement?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Known violations or serious non-compliance",
            "2": "Gaps identified; remediation not started",
            "3": "Generally compliant; minor issues noted in audit",
            "4": "Fully compliant; proactive internal controls",
            "5": "Best-in-class compliance program; clean audit history",
        },
    },
    {
        "id": 28, "key": "financial_strength",
        "name": "Financial strength",
        "explanation": "Struggling with cash flow, or strong margins and financial resources?",
        "type": "qualitative", "format": "descriptor_scale", "unit": None, "direction": "higher_is_better",
        "default_ranges": {
            "1": "Severe cash-flow issues; risk of insolvency",
            "2": "Thin margins; late payments or credit concerns",
            "3": "Stable but modest financial position",
            "4": "Healthy margins and reserves; consistent profitability",
            "5": "Very strong financials; well-capitalized, growing",
        },
    },
]

# ── Category groupings for sidebar navigation ────────────────────────────

CATEGORIES = [
    {
        "label": "Revenue & Growth",
        "icon": "💰",
        "keys": [
            "annual_revenues", "yoy_revenue_growth", "net_new_logo_revenues",
            "pct_revenues_saas", "net_revenue_expansion", "total_revenues",
        ],
    },
    {
        "label": "Sales Performance",
        "icon": "📈",
        "keys": [
            "average_deal_size", "avg_time_to_close", "registered_deals",
            "win_loss_ratio", "partner_generated_opps_pct", "frequency_of_business",
        ],
    },
    {
        "label": "Retention & Satisfaction",
        "icon": "🤝",
        "keys": [
            "renewal_rate", "customer_satisfaction", "communication_with_vendor",
        ],
    },
    {
        "label": "Enablement & Support",
        "icon": "🎓",
        "keys": [
            "mdf_utilization_rate", "quality_of_sales_org",
            "vendor_certifications", "sales_support_calls", "tech_support_calls",
        ],
    },
    {
        "label": "Strategic Fit",
        "icon": "🧭",
        "keys": [
            "dedication_vs_competitive", "dedication_vs_other_vendors",
            "geographical_coverage", "vertical_coverage",
        ],
    },
    {
        "label": "Risk & Governance",
        "icon": "🛡️",
        "keys": [
            "quality_of_management", "known_litigation",
            "export_control_ip", "financial_strength",
        ],
    },
]

METRICS_BY_KEY: dict[str, dict] = {m["key"]: m for m in SCORECARD_METRICS}

SAVE_PATH = pathlib.Path("scoring_criteria.json")

# ─────────────────────────────────────────────────────────────────────────
# 1.  HELPERS
# ─────────────────────────────────────────────────────────────────────────

def _fmt_unit(unit: str | None) -> str:
    """Return a compact display label for the unit."""
    if unit == "$":
        return "$"
    if unit == "%":
        return "%"
    if unit:
        return f" {unit}"
    return ""


def _default_val(val, fallback: str = "") -> str:
    """Turn a numeric default (possibly None) into a string for the input."""
    if val is None:
        return fallback
    return str(val)


def _init_session_state() -> None:
    """Seed st.session_state['criteria'] from disk or defaults."""
    if "criteria" in st.session_state:
        return

    # Try loading saved file first
    if SAVE_PATH.exists():
        try:
            saved = json.loads(SAVE_PATH.read_text())
            st.session_state["criteria"] = saved
            st.session_state["_loaded_from_file"] = True
            return
        except (json.JSONDecodeError, KeyError):
            pass

    # Otherwise build from embedded defaults
    criteria: dict[str, dict] = {}
    for m in SCORECARD_METRICS:
        key = m["key"]
        if m["type"] == "quantitative":
            ranges = {}
            for score in ("1", "2", "3", "4", "5"):
                r = m["default_ranges"][score]
                ranges[score] = {
                    "min": _default_val(r["min"]),
                    "max": _default_val(r["max"]),
                }
            criteria[key] = {
                "name": m["name"],
                "type": m["type"],
                "format": m["format"],
                "unit": m["unit"],
                "direction": m["direction"],
                "ranges": ranges,
            }
        else:
            descs = {}
            for score in ("1", "2", "3", "4", "5"):
                descs[score] = m["default_ranges"][score]
            criteria[key] = {
                "name": m["name"],
                "type": m["type"],
                "format": m["format"],
                "unit": m["unit"],
                "direction": m["direction"],
                "descriptors": descs,
            }
    st.session_state["criteria"] = criteria
    st.session_state["_loaded_from_file"] = False


def _save_criteria() -> None:
    """Persist current session criteria to JSON and session state."""
    SAVE_PATH.write_text(json.dumps(st.session_state["criteria"], indent=2))


def _collect_form_values() -> None:
    """
    Read every widget value from session_state (keyed by widget key)
    back into the criteria dict.  Called on form submit.
    """
    crit = st.session_state["criteria"]
    for m in SCORECARD_METRICS:
        mk = m["key"]
        if m["type"] == "quantitative":
            for s in ("1", "2", "3", "4", "5"):
                min_key = f"{mk}__s{s}_min"
                max_key = f"{mk}__s{s}_max"
                crit[mk]["ranges"][s]["min"] = st.session_state.get(min_key, "")
                crit[mk]["ranges"][s]["max"] = st.session_state.get(max_key, "")
        else:
            for s in ("1", "2", "3", "4", "5"):
                desc_key = f"{mk}__s{s}_desc"
                crit[mk]["descriptors"][s] = st.session_state.get(desc_key, "")
    _save_criteria()


# ─────────────────────────────────────────────────────────────────────────
# 2.  PAGE CONFIG & CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Partner Scorecard — Define Criteria",
    page_icon="📋",
    layout="wide",
)

st.markdown("""
<style>
/* ── General ─────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] { background: #f7f8fb; }
section[data-testid="stSidebar"] { background: #1e2a3a; }
section[data-testid="stSidebar"] * { color: #cfd8e3 !important; }
section[data-testid="stSidebar"] .stRadio label:hover { color: #fff !important; }

/* ── Cards ───────────────────────────────────────────────────────────── */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e6ed;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.metric-card:hover { border-color: #a4b3c9; }

.metric-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.15rem;
}
.metric-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e2a3a;
}
.metric-tag {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.tag-quant { background: #e0ecff; color: #1c5dbf; }
.tag-qual  { background: #f0e6ff; color: #6b3fa0; }
.tag-dir   {
    font-size: 0.7rem; font-weight: 600;
    padding: 2px 9px; border-radius: 20px;
    background: #e8f5e9; color: #2e7d32;
}
.tag-dir-low {
    font-size: 0.7rem; font-weight: 600;
    padding: 2px 9px; border-radius: 20px;
    background: #fff3e0; color: #e65100;
}
.metric-expl {
    font-size: 0.85rem;
    color: #5a6a7e;
    margin-bottom: 0.9rem;
    line-height: 1.45;
}

/* ── Score-level header row ──────────────────────────────────────────── */
.score-header {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;
    width: 28px; height: 28px;
    line-height: 28px;
    text-align: center;
    border-radius: 8px;
    margin-bottom: 4px;
}
.sh-1 { background: #ef5350; }
.sh-2 { background: #ff9800; }
.sh-3 { background: #fdd835; color: #333 !important; }
.sh-4 { background: #66bb6a; }
.sh-5 { background: #2e7d32; }

/* ── Progress counter ────────────────────────────────────────────────── */
.progress-box {
    background: linear-gradient(135deg, #1e2a3a 0%, #2c3e56 100%);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    color: #fff;
    margin-bottom: 1.2rem;
    text-align: center;
}
.progress-box .big { font-size: 2.2rem; font-weight: 800; }
.progress-box .label { font-size: 0.8rem; opacity: 0.75; }

/* ── Toast ───────────────────────────────────────────────────────────── */
.toast-ok {
    background: #2e7d32;
    color: #fff;
    padding: 0.7rem 1.2rem;
    border-radius: 10px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1rem;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from {opacity:0; transform:translateY(-8px);} to {opacity:1; transform:translateY(0);} }

/* ── Tweak Streamlit inputs inside cards ─────────────────────────────── */
.metric-card .stTextInput > div > div > input {
    border-radius: 8px;
    font-size: 0.88rem;
}
.metric-card .stTextArea textarea {
    border-radius: 8px;
    font-size: 0.86rem;
    min-height: 56px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# 3.  INIT STATE & SIDEBAR
# ─────────────────────────────────────────────────────────────────────────

_init_session_state()

with st.sidebar:
    st.markdown("## 📋 Partner Scorecard")
    st.markdown("##### Phase 1 — Scoring Criteria")
    st.markdown("---")

    # Category filter
    cat_labels = ["All Metrics"] + [f"{c['icon']}  {c['label']}" for c in CATEGORIES]
    chosen_cat = st.radio("Jump to category", cat_labels, index=0, label_visibility="collapsed")

    st.markdown("---")

    # Quick stats
    quant_n = sum(1 for m in SCORECARD_METRICS if m["type"] == "quantitative")
    qual_n = len(SCORECARD_METRICS) - quant_n
    st.markdown(
        f"""
        <div class="progress-box">
            <div class="big">{len(SCORECARD_METRICS)}</div>
            <div class="label">METRICS TOTAL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_a, col_b = st.columns(2)
    col_a.metric("Quantitative", quant_n)
    col_b.metric("Qualitative", qual_n)

    st.markdown("---")
    st.caption("Defaults are pre-filled. Edit any value, then click **Save Criteria** at the bottom of the page.")


# ─────────────────────────────────────────────────────────────────────────
# 4.  MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────

st.markdown("# 📋 Define Scoring Criteria")
st.markdown(
    "Configure the **1–5 scoring thresholds** for each partner metric. "
    "Quantitative metrics use numeric ranges; qualitative metrics use text "
    "descriptors. Defaults are pre-filled — adjust to match your business."
)

if st.session_state.get("_just_saved"):
    st.markdown('<div class="toast-ok">✅ Criteria saved successfully to <code>scoring_criteria.json</code></div>', unsafe_allow_html=True)
    st.session_state["_just_saved"] = False

# Determine which metrics to show based on sidebar selection
if chosen_cat == "All Metrics":
    visible_keys = [m["key"] for m in SCORECARD_METRICS]
else:
    # Strip icon prefix to match category label
    cat_name = chosen_cat.split("  ", 1)[-1]
    cat_obj = next(c for c in CATEGORIES if c["label"] == cat_name)
    visible_keys = cat_obj["keys"]

visible_metrics = [METRICS_BY_KEY[k] for k in visible_keys]

# ── Render the form ───────────────────────────────────────────────────

with st.form("criteria_form"):
    for m in visible_metrics:
        mk = m["key"]
        crit = st.session_state["criteria"][mk]
        is_quant = m["type"] == "quantitative"

        type_tag = (
            '<span class="metric-tag tag-quant">Quantitative</span>'
            if is_quant
            else '<span class="metric-tag tag-qual">Qualitative</span>'
        )
        dir_class = "tag-dir" if m["direction"] == "higher_is_better" else "tag-dir-low"
        dir_label = "↑ Higher is better" if m["direction"] == "higher_is_better" else "↓ Lower is better"
        dir_tag = f'<span class="{dir_class}">{dir_label}</span>'

        unit_display = f" ({m['unit']})" if m.get("unit") else ""

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-name">{m['id']}. {m['name']}</span>
                    {type_tag} {dir_tag}
                </div>
                <div class="metric-expl">{m['explanation']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_quant:
            # ── Quantitative: 5 columns of (min, max) ────────────────
            unit_lbl = _fmt_unit(m["unit"])
            cols = st.columns(5)
            for idx, s in enumerate(("1", "2", "3", "4", "5")):
                with cols[idx]:
                    badge_cls = f"sh-{s}"
                    st.markdown(f'<span class="score-header {badge_cls}">{s}</span>', unsafe_allow_html=True)
                    current_min = crit["ranges"][s]["min"]
                    current_max = crit["ranges"][s]["max"]
                    st.text_input(
                        f"Min{unit_display}",
                        value=current_min,
                        key=f"{mk}__s{s}_min",
                        placeholder="No min" if s == "1" else "",
                        label_visibility="visible",
                    )
                    st.text_input(
                        f"Max{unit_display}",
                        value=current_max,
                        key=f"{mk}__s{s}_max",
                        placeholder="No cap" if s == "5" else "",
                        label_visibility="visible",
                    )
        else:
            # ── Qualitative: 5 text-area descriptors ─────────────────
            cols = st.columns(5)
            for idx, s in enumerate(("1", "2", "3", "4", "5")):
                with cols[idx]:
                    badge_cls = f"sh-{s}"
                    st.markdown(f'<span class="score-header {badge_cls}">{s}</span>', unsafe_allow_html=True)
                    current_desc = crit["descriptors"][s]
                    st.text_area(
                        f"Score {s}",
                        value=current_desc,
                        key=f"{mk}__s{s}_desc",
                        height=100,
                        label_visibility="collapsed",
                    )

        st.markdown("")  # spacer between metrics

    # ── Submit button ─────────────────────────────────────────────────
    st.markdown("---")
    col_l, col_mid, col_r = st.columns([2, 2, 1])
    with col_r:
        submitted = st.form_submit_button(
            "💾  Save Criteria",
            use_container_width=True,
            type="primary",
        )

if submitted:
    _collect_form_values()
    st.session_state["_just_saved"] = True
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────
# 5.  FOOTER — preview / download saved JSON
# ─────────────────────────────────────────────────────────────────────────

if SAVE_PATH.exists():
    st.markdown("---")
    st.markdown("#### 📄 Saved Criteria Preview")

    with st.expander("View / download `scoring_criteria.json`", expanded=False):
        raw = SAVE_PATH.read_text()
        st.code(raw, language="json")
        st.download_button(
            label="⬇️  Download JSON",
            data=raw,
            file_name="scoring_criteria.json",
            mime="application/json",
        )
