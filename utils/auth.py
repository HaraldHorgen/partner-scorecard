"""
Authentication module for ChannelPRO™.

Handles password hashing (PBKDF2-SHA256), verification, and user
persistence via a JSON file on the tenant-aware persistent disk.
"""
import hashlib
import json
import secrets

import streamlit as st

from utils.paths import USERS_FILE


# ── Password helpers ────────────────────────────────────────────────────

def hash_pw(pw: str) -> str:
    """Return a ``salt:hash`` string using PBKDF2-SHA256 (200 000 iters)."""
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000)
    return f"{salt}:{h.hex()}"


def verify_pw(pw: str, stored: str) -> bool:
    """Verify *pw* against a ``salt:hash`` string produced by :func:`hash_pw`."""
    try:
        salt, h = stored.split(":")
        return (
            hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex()
            == h
        )
    except Exception:
        return False


# ── User persistence ───────────────────────────────────────────────────

def load_users() -> dict:
    """Load the user database from disk, creating a default admin if absent."""
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except Exception:
            pass
    default = {
        "admin": {
            "password_hash": hash_pw("admin"),
            "display_name": "Administrator",
            "role": "admin",
            "tenant": None,
        }
    }
    save_users(default)
    return default


def save_users(users: dict) -> None:
    """Persist the user database to disk."""
    USERS_FILE.write_text(json.dumps(users, indent=2))


# ── Login flow ──────────────────────────────────────────────────────────

def handle_login() -> bool:
    """Render the login form and authenticate the user.

    Returns ``True`` if the user is now authenticated (caller should
    proceed to the main app), or calls ``st.stop()`` to halt execution
    when credentials are missing / invalid.
    """
    from utils.paths import all_tenants  # deferred to avoid circular import
    from utils.ui import YORK_LOGO_B64, LOGIN_BG_B64

    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None

    if st.session_state["auth_user"] is not None:
        return True  # already logged in

    # ── render login page ───────────────────────────────────────────
    st.markdown(
        f"""<style>
        [data-testid="stAppViewContainer"]{{background:url('data:image/jpeg;base64,{LOGIN_BG_B64}') center center/cover no-repeat fixed !important}}
        [data-testid="stAppViewContainer"]::before{{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(10,18,36,0.45);z-index:0;pointer-events:none}}
        [data-testid="stMainBlockContainer"]{{max-width:400px !important;margin:0 auto !important;padding-top:4vh !important}}
        [data-testid="stForm"]{{background:rgba(255,255,255,0.95);border-radius:0 0 16px 16px;padding:28px 32px 32px 32px;box-shadow:0 4px 24px rgba(0,0,0,.25);backdrop-filter:blur(10px);border:none}}
        [data-testid="stForm"] [data-testid="stFormSubmitButton"] button{{background:#e85b5b;border-color:#e85b5b}}
        .stCaption{{text-align:center}}
        .stAlert{{text-align:center}}
        </style>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div style="background:rgba(255,255,255,0.95);border-radius:16px 16px 0 0;padding:36px 32px 8px 32px;box-shadow:0 -4px 24px rgba(0,0,0,.15);backdrop-filter:blur(10px)">
            <div style="text-align:center;margin-bottom:8px;">
                <img src="data:image/jpeg;base64,{YORK_LOGO_B64}" style="height:50px;margin-bottom:12px;"><br>
                <span style="font-size:1.4rem;font-weight:800;color:#1e2a3a;">ChannelPRO\u2122</span><br>
                <span style="font-size:.88rem;color:#4a6a8f;">Partner Revenue Optimizer</span>
            </div></div>""",
        unsafe_allow_html=True,
    )

    users = load_users()
    with st.form("login_form"):
        uname = st.text_input("Username", placeholder="Enter your username")
        pw = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button(
            "Sign In", use_container_width=True, type="primary"
        )

    if submitted:
        if uname in users and verify_pw(pw, users[uname]["password_hash"]):
            st.session_state["auth_user"] = uname
            u = users[uname]
            st.session_state["auth_role"] = u["role"]
            st.session_state["auth_display"] = u["display_name"]
            st.session_state["auth_tenant"] = u.get("tenant")
            if u["role"] == "admin":
                tenants = all_tenants()
                st.session_state["active_tenant"] = tenants[0] if tenants else None
            else:
                st.session_state["active_tenant"] = u["tenant"]
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.caption("Default admin login: **admin** / **admin** — change this after first login!")
    st.stop()
    return False  # unreachable, but explicit for type checkers
