"""
Shared UI helpers — branding, CSS, and logo rendering for ChannelPRO™.
"""
import json

import streamlit as st

from utils.assets import LOGIN_BG_B64, YORK_LOGO_B64  # noqa: F401 (re-exported)
from utils.paths import client_path

# Re-export so other modules can do ``from utils.ui import YORK_LOGO_B64``
__all__ = ["YORK_LOGO_B64", "LOGIN_BG_B64", "inject_css", "logo", "brand"]


# ── CSS injection ──────────────────────────────────────────────────────

def inject_css() -> None:
    """Inject the global ChannelPRO™ stylesheet (call once per page load)."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;800&display=swap');
[data-testid="stAppViewContainer"]{background:#f3f5f9;font-family:'DM Sans',sans-serif}
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
[data-testid="stAppViewContainer"] input[type="text"],[data-testid="stAppViewContainer"] textarea{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important}
[data-testid="stAppViewContainer"] input[type="text"]:focus,[data-testid="stAppViewContainer"] textarea:focus{background:#fff!important;border-color:#2563eb!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div{background:#e8ebf1!important;border:1.5px solid #b0bdd0!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div:focus-within{background:#fff!important;border-color:#2563eb!important}
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
