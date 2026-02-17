"""
Tenant-aware path management for ChannelPRO™.

All data is isolated per-tenant under BASE_DIR/tenants/<tenant_id>/.
BASE_DIR defaults to the RENDER_DISK_PATH env var (persistent disk on Render)
or the current working directory for local development.
"""
import os
import pathlib

import streamlit as st

# ── Root directories ────────────────────────────────────────────────────
BASE_DIR = pathlib.Path(os.environ.get("RENDER_DISK_PATH", "."))
BASE_DIR.mkdir(parents=True, exist_ok=True)

USERS_FILE = BASE_DIR / "users.json"

TENANTS_DIR = BASE_DIR / "tenants"
TENANTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Tenant helpers ──────────────────────────────────────────────────────

def tenant_dir(tid: str) -> pathlib.Path:
    """Return (and create) the data directory for a given tenant ID."""
    d = TENANTS_DIR / tid
    d.mkdir(parents=True, exist_ok=True)
    return d


def all_tenants() -> list[str]:
    """Return a sorted list of all tenant IDs that have directories."""
    if not TENANTS_DIR.exists():
        return []
    return sorted([d.name for d in TENANTS_DIR.iterdir() if d.is_dir()])


def current_data_dir() -> pathlib.Path:
    """Return the data directory for the currently active tenant."""
    tid = st.session_state.get("active_tenant")
    return tenant_dir(tid) if tid else BASE_DIR


# ── Per-tenant file paths ──────────────────────────────────────────────

def save_path() -> pathlib.Path:
    """Path to scoring_criteria.json for the active tenant."""
    return current_data_dir() / "scoring_criteria.json"


def client_path() -> pathlib.Path:
    """Path to client_info.json for the active tenant."""
    return current_data_dir() / "client_info.json"


def csv_path() -> pathlib.Path:
    """Path to all_partners.csv for the active tenant."""
    return current_data_dir() / "all_partners.csv"


def class_path() -> pathlib.Path:
    """Path to classification_config.json for the active tenant."""
    return current_data_dir() / "classification_config.json"


def raw_path() -> pathlib.Path:
    """Path to all_partners_raw.json for the active tenant."""
    return current_data_dir() / "all_partners_raw.json"


def tenant_config_path(tid: str | None = None) -> pathlib.Path:
    """Path to tenant_config.json (optionally for a specific tenant)."""
    if tid:
        return tenant_dir(tid) / "tenant_config.json"
    return current_data_dir() / "tenant_config.json"


def be_path() -> pathlib.Path:
    """Path to break_even_configs.json for the active tenant."""
    return current_data_dir() / "break_even_configs.json"


def sd_path() -> pathlib.Path:
    """Path to support_data.csv for the active tenant."""
    return current_data_dir() / "support_data.csv"
