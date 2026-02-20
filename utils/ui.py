"""
Shared UI helpers — branding, CSS, and logo rendering for ChannelPRO™.
"""
import json

import streamlit as st

from utils.assets import LOGIN_BG_B64, YORK_LOGO_B64  # noqa: F401 (re-exported)
from utils.paths import client_path

# Re-export so other modules can do ``from utils.ui import YORK_LOGO_B64``
__all__ = [
    "YORK_LOGO_B64", "LOGIN_BG_B64", "inject_css", "logo", "brand",
    "display_styled_assessment_table",
    "display_classification_dashboard",
    "get_tenant_tier", "show_premium_placeholder",
]


# ── Short display names for metric columns ────────────────────────────
# Keeps headers compact inside grouped columns so users don't need to
# scroll excessively.  Full names are available as header tooltips.
_METRIC_SHORT_NAMES: dict[str, str] = {
    "annual_revenues":           "Annual Rev",
    "yoy_revenue_growth":        "YoY Growth",
    "net_new_logo_revenues":     "New Logo Rev",
    "pct_revenues_saas":         "% SaaS Rev",
    "net_revenue_expansion":     "Net Expansion",
    "total_revenues":            "Total Rev",
    "avg_deal_size_net_new":     "Deal (New)",
    "avg_deal_size_renewals":    "Deal (Renew)",
    "avg_time_to_close":         "Time to Close",
    "registered_deals":          "Reg Deals",
    "win_loss_ratio":            "Win / Loss",
    "partner_generated_opps_pct":"Partner Opps %",
    "frequency_of_business":     "Frequency",
    "renewal_rate":              "Renewal Rate",
    "customer_satisfaction":      "Cust Sat",
    "communication_with_vendor": "Communication",
    "mdf_utilization_rate":      "MDF Util",
    "quality_of_sales_org":      "Sales Org",
    "vendor_certifications":     "Certs",
    "sales_support_calls":       "Sales Support",
    "tech_support_calls":        "Tech Support",
    "dedication_vs_competitive": "vs Competitors",
    "dedication_vs_other_vendors":"vs Vendors",
    "geographical_coverage":     "Geo Coverage",
    "vertical_coverage":         "Vertical Cov",
    "quality_of_management":     "Mgmt Quality",
    "known_litigation":          "Litigation",
    "export_control_ip":         "Export / IP",
    "financial_strength":        "Fin Strength",
}


# ── CSS injection ──────────────────────────────────────────────────────

def inject_css() -> None:
    """Inject the global ChannelPRO™ stylesheet (call once per page load)."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"]{background:#f3f5f9;font-family:'DM Sans',sans-serif;color:#1e2a3a}
[data-testid="stAppViewContainer"] label,[data-testid="stAppViewContainer"] .stRadio label,[data-testid="stAppViewContainer"] .stCheckbox label,[data-testid="stAppViewContainer"] .stMultiSelect label,[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"]{color:#1e2a3a!important}
section[data-testid="stSidebar"]{background:linear-gradient(195deg,#162033,#1e2d45)}
section[data-testid="stSidebar"] *{color:#c4cfde!important}
section[data-testid="stSidebar"] hr{border-color:#2a3d57!important}
.info-box{background:#f0f2f7;border-left:4px solid #2563eb;border-radius:8px;padding:22px 26px;margin:20px 0 28px;line-height:1.7;color:#000000;font-size:.92rem}
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
[data-testid="stAppViewContainer"] input[type="text"],[data-testid="stAppViewContainer"] input[type="number"],[data-testid="stAppViewContainer"] textarea{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important;color:#1e2a3a!important}
[data-testid="stAppViewContainer"] input[type="text"]:focus,[data-testid="stAppViewContainer"] input[type="number"]:focus,[data-testid="stAppViewContainer"] textarea:focus{background:#fff!important;border-color:#2563eb!important;color:#1e2a3a!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important;color:#1e2a3a!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div:focus-within{background:#fff!important;border-color:#2563eb!important;color:#1e2a3a!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] span,[data-testid="stAppViewContainer"] [data-baseweb="select"] input{color:#1e2a3a!important}
[data-testid="stAppViewContainer"] [data-baseweb="tag"]{color:#1e2a3a!important}
[data-testid="stAppViewContainer"] .stSelectbox div[data-baseweb="select"] div,[data-testid="stAppViewContainer"] .stMultiSelect div[data-baseweb="select"] div{color:#1e2a3a!important}
.hm-tbl{width:100%;border-collapse:collapse;font-size:.82rem;background:#fff;margin:1rem 0}
.hm-tbl th{background:#1e2a3a;color:#fff;padding:8px 6px;text-align:center;font-weight:700;font-size:.72rem;text-transform:uppercase;white-space:nowrap;border:1px solid #2a3d57}
.hm-tbl th.hm-diag{white-space:nowrap;vertical-align:bottom;height:160px;padding:0;width:40px;min-width:40px;text-align:left}
.hm-tbl th.hm-diag > div{display:inline-block;white-space:nowrap;transform:rotate(-55deg);transform-origin:0 100%;width:max-content;padding-bottom:6px;margin-left:22px;font-size:.7rem;line-height:1}
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
.login-box{max-width:420px;margin:0 auto;background:rgba(255,255,255,0.95);border-radius:16px;padding:40px;box-shadow:0 4px 24px rgba(0,0,0,.25);backdrop-filter:blur(10px)}
.tenant-badge{display:inline-block;padding:4px 12px;border-radius:8px;font-size:.82rem;font-weight:700;background:#2563eb;color:#fff;margin-bottom:8px}
.plist-item{display:flex;align-items:center;justify-content:space-between;padding:8px 14px;border:1px solid #e2e6ed;border-radius:8px;margin:4px 0;background:#fff;font-size:.88rem}
section[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:#dc4040!important;border-color:#dc4040!important;color:#fff!important;font-weight:800!important}
</style>
""",
        unsafe_allow_html=True,
    )


# ── Branding ───────────────────────────────────────────────────────────

def logo() -> None:
    """Render the small ChannelPRO™ logo in the sidebar."""
    st.markdown(
        f'<img src="data:image/jpeg;base64,{YORK_LOGO_B64}" '
        f'style="height:50px;margin-bottom:8px;">',
        unsafe_allow_html=True,
    )


def brand() -> None:
    """Render the full header bar with ChannelPRO™ branding and optional client logo."""
    logo_url = ""
    cp = client_path()
    if cp.exists():
        try:
            disk_ci = json.loads(cp.read_text())
            logo_url = disk_ci.get("logo_url", "")
        except Exception:
            pass
    if not logo_url:
        logo_url = st.session_state.get("client_info", {}).get("logo_url", "")

    brand_html = (
        f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">'
        f'<img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;border-radius:6px;">'
        f'<div><div style="font-size:1.6rem;font-weight:800;color:#1e2a3a;">ChannelPRO\u2122</div>'
        f'<div style="font-size:.92rem;color:#4a6a8f;font-weight:600;margin-top:-4px;">Partner Revenue Optimizer</div></div></div>'
    )

    if logo_url:
        left_col, right_col = st.columns([5, 1])
        with left_col:
            st.markdown(brand_html, unsafe_allow_html=True)
        with right_col:
            try:
                st.image(logo_url, width=80)
            except Exception:
                pass
    else:
        st.markdown(brand_html, unsafe_allow_html=True)


# ── Tenant tier detection ─────────────────────────────────────────────

def get_tenant_tier(tenant_id: str | None = None) -> str:
    """Return the access tier for a tenant based on its ID prefix.

    Returns one of ``"admin"``, ``"client"``, or ``"demo"``.
    """
    if tenant_id is None:
        tenant_id = st.session_state.get("active_tenant") or ""
    if st.session_state.get("auth_role") == "admin":
        return "admin"
    tid = (tenant_id or "").lower()
    if tid.startswith("demo_"):
        return "demo"
    return "client"


def show_premium_placeholder(feature_name: str) -> None:
    """Render a professional locked-module placeholder and halt."""
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 40px; border-radius: 15px;
                    border-left: 5px solid #00d4ff; text-align: center;">
            <h2 style="color: #0e1117;">\U0001f512 {feature_name} is a Premium Module</h2>
            <p style="font-size: 1.1em; color: #31333F;">
                This advanced strategic module is reserved for full <b>ChannelPRO\u2122</b> engagements.
                Unlock high-resolution partner classification and automated realignment roadmaps.
            </p>
            <div style="margin-top: 25px;">
                <a href="mailto:hhorgen@theyorkgroup.com?subject=Unlocking {feature_name}"
                   style="background-color: #00d4ff; color: white; padding: 12px 25px;
                          text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Contact The York Group to Unlock
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ── Professional AG Grid assessment table ─────────────────────────────

def display_styled_assessment_table(df_grid, enabled_metrics):
    """Render the Partner Assessment table with Alpine-themed AG Grid.

    Args:
        df_grid: DataFrame with columns — Partner, Country, Tier, Discount,
                 PAM, [metric name columns …], Total, Pct, Grade.
        enabled_metrics: list of enabled metric dicts (each with ``key``,
                         ``name``, ``explanation``, ``cat``).

    Returns:
        The ``AgGrid`` response object (for row-selection handling by the
        caller).

    UX Rationale
    -------------
    • **Font sizes** — Data cells at 0.80 rem provide dense-but-readable
      scanning across up to 29 metrics.  Headers at 0.72 rem uppercase
      create a clear visual hierarchy without dominating the data rows.
    • **Cell padding** — 6–8 px vertical padding balances information
      density with comfortable click targets and visual breathing room.
    • **Column groups** — Chunking metrics into 6 named categories
      (Revenue & Growth, Sales Performance, …) reduces cognitive load.
      Users can mentally skip entire groups that aren't relevant.
    • **Pinned columns** — *Partner* (left) and *Total / Score % / Grade*
      (right) remain visible during horizontal scroll so the user always
      has context and summary in view.
    • **Colour scales** — Pastel washes (not saturated blocks) reduce eye
      strain during prolonged analysis while preserving quick-scan
      "traffic light" semantics.  Soft ambers and greens replace the
      previous neon palette.
    • **Alpine theme** — AG Grid's Alpine theme provides a modern, light
      UI foundation with refined borders and spacing that matches
      contemporary B2B SaaS dashboards.
    """
    from st_aggrid import (
        AgGrid, GridOptionsBuilder, JsCode,
        GridUpdateMode, ColumnsAutoSizeMode,
    )
    from utils.scoring import CATEGORIES

    # ── Lookup helpers ──
    em_key_to_name = {m["key"]: m["name"] for m in enabled_metrics}

    # ── JsCode: professional pastel heatmap for scores 1–5 ──
    metric_cell_style = JsCode("""
    function(params) {
        var s = {'textAlign':'center','fontWeight':'700',
                 'fontFamily':"'JetBrains Mono',monospace",'fontSize':'0.80rem'};
        if (params.value==null||params.value===undefined||params.value===0){
            s['color']='#CBD5E1'; return s;}
        var v=parseInt(params.value);
        if      (v===1){s['backgroundColor']='#FEE2E2';s['color']='#991B1B';}
        else if (v===2){s['backgroundColor']='#FEF3C7';s['color']='#92400E';}
        else if (v===3){s['backgroundColor']='#FEF9C3';s['color']='#854D0E';}
        else if (v===4){s['backgroundColor']='#DCFCE7';s['color']='#166534';}
        else if (v===5){s['backgroundColor']='#BBF7D0';s['color']='#14532D';}
        else           {s['color']='#64748B';}
        return s;
    }
    """)

    # ── JsCode: grade badge ──
    grade_cell_style = JsCode("""
    function(params) {
        var g=params.value, bg='#DC2626', fg='#fff';
        if      (g==='A') {bg='#166534';}
        else if (g==='B+'){bg='#15803D';}
        else if (g==='B') {bg='#65A30D';}
        else if (g==='C+'){bg='#CA8A04';}
        else if (g==='C') {bg='#D97706';}
        return {'backgroundColor':bg,'color':fg,'textAlign':'center',
                'fontWeight':'800','fontFamily':"'JetBrains Mono',monospace",
                'fontSize':'0.82rem','borderRadius':'4px'};
    }
    """)

    # ── JsCode: summary columns (Total, Score %) — blue accent ──
    summary_cell_style = JsCode("""
    function(params) {
        return {'backgroundColor':'#DBEAFE','color':'#1E40AF','textAlign':'center',
                'fontWeight':'800','fontFamily':"'JetBrains Mono',monospace",
                'fontSize':'0.82rem'};
    }
    """)

    # ── JsCode: value formatters ──
    metric_formatter = JsCode("""
    function(params) {
        if (params.value==null||params.value===undefined||params.value===0) return '\u2014';
        return params.value;
    }
    """)
    pct_formatter = JsCode("""
    function(params) {
        if (params.value==null||params.value===undefined) return '0.0%';
        return params.value.toFixed(1)+'%';
    }
    """)

    # ── Build grid options via GridOptionsBuilder ──
    gb = GridOptionsBuilder.from_dataframe(df_grid)

    gb.configure_default_column(
        filterable=True, sortable=True, resizable=True,
        floatingFilter=True, minWidth=70, suppressMenu=False,
        wrapHeaderText=True, autoHeaderHeight=True,
    )

    # --- Info columns (pinned left) ---
    gb.configure_column(
        "Partner", pinned="left", minWidth=180, maxWidth=280,
        filter="agTextColumnFilter",
        cellStyle={"textAlign": "left", "fontWeight": "600",
                   "color": "#1E293B", "paddingLeft": "12px"},
    )
    gb.configure_column("Country", minWidth=100, maxWidth=140,
                        filter="agTextColumnFilter")
    gb.configure_column("Tier", minWidth=80, maxWidth=120,
                        filter="agSetColumnFilter")
    gb.configure_column("Discount", minWidth=90, maxWidth=120,
                        filter="agTextColumnFilter")
    gb.configure_column("PAM", minWidth=140, maxWidth=200,
                        filter="agTextColumnFilter",
                        cellStyle={"textAlign": "left"})

    # --- Metric columns (short display names, heatmap styling) ---
    for m in enabled_metrics:
        short = _METRIC_SHORT_NAMES.get(m["key"], m["name"])
        gb.configure_column(
            m["name"],
            header_name=short,
            type=["numericColumn"],
            filter="agNumberColumnFilter",
            cellStyle=metric_cell_style,
            valueFormatter=metric_formatter,
            minWidth=78, maxWidth=130,
            headerTooltip=f'{m["name"]} \u2014 {m["explanation"]}',
        )

    # --- Summary columns (pinned right) ---
    gb.configure_column(
        "Total", pinned="right", type=["numericColumn"],
        filter="agNumberColumnFilter", cellStyle=summary_cell_style,
        minWidth=72, maxWidth=90, sort="desc",
    )
    gb.configure_column(
        "Pct", pinned="right", header_name="Score %",
        type=["numericColumn"], filter="agNumberColumnFilter",
        cellStyle=summary_cell_style, valueFormatter=pct_formatter,
        minWidth=82, maxWidth=100,
    )
    gb.configure_column(
        "Grade", pinned="right", filter="agSetColumnFilter",
        cellStyle=grade_cell_style, minWidth=75, maxWidth=90,
    )

    # Pagination for large datasets
    if len(df_grid) > 50:
        gb.configure_pagination(paginationAutoPageSize=False,
                                paginationPageSize=50)

    # Row selection
    gb.configure_selection(selection_mode="single", use_checkbox=False)

    # Grid-level options
    gb.configure_grid_options(groupHeaderHeight=36, rowHeight=38)

    grid_options = gb.build()

    # ── Post-process: wrap metric columns in category groups ──
    original_cols = grid_options["columnDefs"]
    col_by_field = {c["field"]: c for c in original_cols}

    # Info columns (left side, ungrouped)
    info_fields = ["Partner", "Country", "Tier", "Discount", "PAM"]
    info_cols = [col_by_field[f] for f in info_fields if f in col_by_field]

    # Summary columns (right side, ungrouped)
    summary_fields = ["Total", "Pct", "Grade"]
    summary_cols = [col_by_field[f] for f in summary_fields
                    if f in col_by_field]

    # Metric columns grouped by category
    placed_names: set[str] = set()
    grouped_cols: list[dict] = []
    for cat in CATEGORIES:
        children = []
        for key in cat["keys"]:
            name = em_key_to_name.get(key)
            if name and name in col_by_field:
                children.append(col_by_field[name])
                placed_names.add(name)
        if children:
            grouped_cols.append({
                "headerName": f'{cat["icon"]}  {cat["label"]}',
                "marryChildren": True,
                "children": children,
            })

    # Safety net: any enabled metric not covered by CATEGORIES
    orphan_cols = [
        col_by_field[m["name"]]
        for m in enabled_metrics
        if m["name"] not in placed_names and m["name"] in col_by_field
    ]

    grid_options["columnDefs"] = (
        info_cols + grouped_cols + orphan_cols + summary_cols
    )

    # ── Custom CSS — Alpine theme refinements ──
    custom_css = {
        # Category group header row
        ".ag-header-group-cell": {
            "background-color": "#F1F5F9 !important",
            "color": "#334155 !important",
            "font-weight": "700 !important",
            "font-size": "0.74rem",
            "text-transform": "uppercase",
            "letter-spacing": "0.04em",
            "border-bottom": "2px solid #CBD5E1 !important",
        },
        # Individual column headers
        ".ag-header-cell": {
            "background-color": "#F8FAFC !important",
            "color": "#475569 !important",
            "font-weight": "600",
            "font-size": "0.72rem",
        },
        ".ag-header-cell-label": {
            "font-size": "0.72rem",
            "font-weight": "600",
        },
        # Zebra striping
        ".ag-row-even": {"background-color": "#FFFFFF"},
        ".ag-row-odd": {"background-color": "#F8FAFC"},
        ".ag-row:hover": {"background-color": "#EFF6FF !important"},
        # Grid wrapper
        ".ag-root-wrapper": {
            "border-radius": "10px",
            "border": "1px solid #E2E8F0",
            "font-family": "'DM Sans', sans-serif",
            "box-shadow": "0 1px 3px rgba(0,0,0,0.04)",
        },
        # Floating filter styling
        ".ag-floating-filter-input": {"font-size": "0.76rem"},
        # Pinned-column visual separators
        ".ag-pinned-left-cols-container": {
            "border-right": "2px solid #CBD5E1 !important",
        },
        ".ag-pinned-right-cols-container": {
            "border-left": "2px solid #CBD5E1 !important",
        },
        # Pinned header backgrounds
        ".ag-pinned-left-header": {
            "background-color": "#F1F5F9 !important",
        },
        ".ag-pinned-right-header": {
            "background-color": "#EFF6FF !important",
        },
    }

    # ── Grid height ──
    grid_height = min(max(len(df_grid) * 38 + 140, 420), 780)

    # ── Render ──
    return AgGrid(
        df_grid,
        gridOptions=grid_options,
        custom_css=custom_css,
        height=grid_height,
        theme="alpine",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=True,
        key="p3_aggrid",
    )


# ── Classification executive dashboard ────────────────────────────────

def display_classification_dashboard(partners, classification):
    """Render a dual-visual executive summary above the classification table.

    Left column: **Boston Matrix** (BCG-style 2×2 scatter) mapping every
    classified partner by *Annual Revenue* score (X) vs *Net-New Logo
    Revenue* score (Y).  Background quadrants are shaded and labelled
    Stars / Question Marks / Cash Cows / Dogs.

    Right column: **Donut chart** showing the percentage of partners in
    each of the four classification categories.

    Both charts use the Plotly interactive toolbar so users can zoom, pan,
    and download images (PNG) directly.

    Args:
        partners: list of partner dicts (from ``_load_partners``).
        classification: dict mapping ``partner_name → quadrant_number``
                        (1–4), as returned by ``classify_partners``.
    """
    import random

    import plotly.graph_objects as go

    from utils.scoring import Q_LABELS

    # ── Build working rows ──────────────────────────────────────────
    rows: list[dict] = []
    for p in partners:
        name = p.get("partner_name", "")
        if name not in classification:
            continue
        qn = classification[name]
        try:
            rev = int(p.get("annual_revenues", 0) or 0)
        except (TypeError, ValueError):
            rev = 0
        try:
            nnl = int(p.get("net_new_logo_revenues", 0) or 0)
        except (TypeError, ValueError):
            nnl = 0
        try:
            total = int(p.get("total_score", 0) or 0)
        except (TypeError, ValueError):
            total = 0
        try:
            pct = float(p.get("percentage", 0) or 0)
        except (TypeError, ValueError):
            pct = 0.0
        rows.append({
            "Partner": name, "Revenue": rev, "New Logos": nnl,
            "Quadrant": qn, "Total": total, "Pct": pct,
        })

    if not rows:
        return

    # Counts per quadrant
    by_q: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in rows:
        by_q[r["Quadrant"]] = by_q.get(r["Quadrant"], 0) + 1

    # ── Plotly config shared by both charts ─────────────────────────
    _plotly_cfg: dict = {
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {
            "format": "png", "height": 600, "width": 800, "scale": 2,
        },
    }

    # ── BOSTON MATRIX (scatter) ──────────────────────────────────────
    scatter = go.Figure()

    # Quadrant background rectangles (subtle pastel fills)
    _qshapes = [
        # top-left: Question Marks
        dict(x0=0.5, x1=3, y0=3, y1=5.5, fc="rgba(59,130,246,0.08)"),
        # top-right: Stars
        dict(x0=3, x1=5.5, y0=3, y1=5.5, fc="rgba(251,191,36,0.10)"),
        # bottom-left: Dogs
        dict(x0=0.5, x1=3, y0=0.5, y1=3, fc="rgba(156,163,175,0.08)"),
        # bottom-right: Cash Cows
        dict(x0=3, x1=5.5, y0=0.5, y1=3, fc="rgba(34,197,94,0.08)"),
    ]
    for s in _qshapes:
        scatter.add_shape(
            type="rect", x0=s["x0"], x1=s["x1"], y0=s["y0"], y1=s["y1"],
            fillcolor=s["fc"], line=dict(width=0), layer="below",
        )

    # Midpoint dividers
    scatter.add_hline(y=3, line_dash="dot", line_color="#CBD5E1", line_width=1)
    scatter.add_vline(x=3, line_dash="dot", line_color="#CBD5E1", line_width=1)

    # Quadrant labels (BCG terminology)
    _qlabels = [
        (1.75, 5.3, "\u2753 Question Marks", "#3B82F6"),
        (4.25, 5.3, "\u2B50 Stars",          "#D97706"),
        (1.75, 0.7, "\U0001F415 Dogs",       "#9CA3AF"),
        (4.25, 0.7, "\U0001F404 Cash Cows",  "#16A34A"),
    ]
    for lx, ly, ltxt, lc in _qlabels:
        scatter.add_annotation(
            x=lx, y=ly, text=ltxt, showarrow=False,
            font=dict(size=11, color=lc, family="DM Sans"),
        )

    # Partner dots — one trace per quadrant for legend grouping
    random.seed(42)  # deterministic jitter for stable layout
    show_text = len(rows) <= 15

    for qn in (1, 2, 3, 4):
        ql, qc = Q_LABELS.get(qn, (f"Q{qn}", "#666"))
        q_rows = [r for r in rows if r["Quadrant"] == qn]
        if not q_rows:
            continue
        x_vals = [r["Revenue"]   + random.uniform(-0.18, 0.18) for r in q_rows]
        y_vals = [r["New Logos"] + random.uniform(-0.18, 0.18) for r in q_rows]
        names  = [r["Partner"] for r in q_rows]

        scatter.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode="markers+text" if show_text else "markers",
            name=f"Q{qn}: {ql}",
            text=names if show_text else None,
            textposition="top center",
            textfont=dict(size=9, color="#475569"),
            marker=dict(
                color=qc, size=11, opacity=0.85,
                line=dict(width=1.5, color="#FFFFFF"),
            ),
            customdata=[
                [r["Partner"], r["Revenue"], r["New Logos"],
                 r["Total"], r["Pct"]]
                for r in q_rows
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Revenue Score: %{customdata[1]}<br>"
                "New Logo Score: %{customdata[2]}<br>"
                "Total: %{customdata[3]}  (%{customdata[4]:.1f}%)"
                "<extra>Q" + str(qn) + ": " + ql + "</extra>"
            ),
        ))

    scatter.update_layout(
        title=dict(
            text="Boston Matrix",
            font=dict(size=15, color="#1E293B", family="DM Sans"),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(
            title="Annual Revenue Score", range=[0.3, 5.7], dtick=1,
            gridcolor="#F1F5F9", zeroline=False,
        ),
        yaxis=dict(
            title="Net-New Logo Score", range=[0.3, 5.7], dtick=1,
            gridcolor="#F1F5F9", zeroline=False,
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="DM Sans, sans-serif", size=12),
        height=440,
        margin=dict(l=50, r=20, t=50, b=80),
        legend=dict(
            orientation="h", yanchor="top", y=-0.15,
            xanchor="center", x=0.5, font=dict(size=10),
        ),
        hoverlabel=dict(
            bgcolor="white", font_size=12, font_family="DM Sans",
        ),
    )

    # ── DONUT CHART ─────────────────────────────────────────────────
    pie_labels, pie_values, pie_colors = [], [], []
    for qn in (1, 2, 3, 4):
        ql, qc = Q_LABELS.get(qn, (f"Q{qn}", "#666"))
        pie_labels.append(f"Q{qn}: {ql}")
        pie_values.append(by_q.get(qn, 0))
        pie_colors.append(qc)

    donut = go.Figure(go.Pie(
        labels=pie_labels,
        values=pie_values,
        marker=dict(
            colors=pie_colors,
            line=dict(color="#FFFFFF", width=2),
        ),
        hole=0.45,
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=11, family="DM Sans"),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Partners: %{value}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
        pull=[0.03] * 4,
    ))

    # Total count in the donut hole
    donut.add_annotation(
        text=(
            f"<b>{sum(pie_values)}</b><br>"
            "<span style='font-size:10px;color:#64748B'>partners</span>"
        ),
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=24, color="#1E293B", family="JetBrains Mono"),
    )

    donut.update_layout(
        title=dict(
            text="Distribution by Category",
            font=dict(size=15, color="#1E293B", family="DM Sans"),
            x=0.5, xanchor="center",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="DM Sans, sans-serif"),
        height=440,
        margin=dict(l=20, r=20, t=50, b=40),
        showlegend=False,
    )

    # ── Render side-by-side ─────────────────────────────────────────
    col_l, col_r = st.columns([1, 1])
    with col_l:
        _plotly_cfg["toImageButtonOptions"]["filename"] = "boston_matrix"
        st.plotly_chart(scatter, use_container_width=True, config=_plotly_cfg)
    with col_r:
        _plotly_cfg["toImageButtonOptions"]["filename"] = "classification_dist"
        st.plotly_chart(donut, use_container_width=True, config=_plotly_cfg)

    # Helpful note if axis metrics are unscored
    has_data = any(r["Revenue"] > 0 or r["New Logos"] > 0 for r in rows)
    if not has_data:
        st.caption(
            "\u2139\ufe0f  Enable and score **Annual revenues** and "
            "**Net-new logo revenues** in Step 2 to position partners "
            "on the Boston Matrix."
        )
