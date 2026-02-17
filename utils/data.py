"""
Data loading and persistence for ChannelPRO™.

Uses ``@st.cache_data`` where appropriate to avoid redundant I/O on
CSV and JSON files during a single Streamlit script run.
"""
import csv
import json
import pathlib
import re

import streamlit as st

from utils.paths import (
    be_path,
    class_path,
    csv_path,
    raw_path,
    tenant_config_path,
)


# ── Helpers ─────────────────────────────────────────────────────────────

def _sf(val):
    """Coerce a string value to float, stripping currency/percent symbols."""
    if val is None:
        return None
    c = re.sub(r"[,$%\s]", "", str(val).strip())
    if c == "":
        return None
    try:
        return float(c)
    except ValueError:
        return None


# ── Cached CSV loading ──────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_partners_cached(_path_str: str) -> list[dict]:
    """Load partners from a CSV file with a 30-second TTL cache.

    The *_path_str* parameter is a string (not a Path) because
    ``@st.cache_data`` requires hashable arguments.  The leading
    underscore tells Streamlit not to hash the parameter name.
    """
    p = pathlib.Path(_path_str)
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def load_partners(path: pathlib.Path | None = None) -> list[dict]:
    """Public wrapper — resolves the default path, then delegates to cache."""
    cp = path or csv_path()
    return load_partners_cached(str(cp))


def invalidate_partner_cache() -> None:
    """Clear the partner CSV cache after writes."""
    load_partners_cached.clear()


# ── Raw partner data (JSON) ────────────────────────────────────────────

def load_raw() -> list[dict]:
    """Load the raw (pre-scored) partner data list."""
    rp = raw_path()
    if rp.exists():
        try:
            return json.loads(rp.read_text())
        except Exception:
            pass
    return []


def save_raw(partner_raw: dict) -> None:
    """Upsert a single partner's raw data into the raw JSON file."""
    rp = raw_path()
    all_raw = json.loads(rp.read_text()) if rp.exists() else []
    found = False
    for i, r in enumerate(all_raw):
        if r.get("partner_name") == partner_raw.get("partner_name"):
            all_raw[i] = partner_raw
            found = True
            break
    if not found:
        all_raw.append(partner_raw)
    rp.write_text(json.dumps(all_raw, indent=2))


# ── Partner CRUD ────────────────────────────────────────────────────────

def append_partner(row_dict: dict, raw_dict: dict, enabled_metrics: list) -> None:
    """Append a scored partner row to the CSV and save its raw data."""
    fnames = [
        "partner_name", "partner_year", "partner_tier", "partner_discount",
        "partner_city", "partner_country", "pam_name", "pam_email",
    ]
    fnames += [m["key"] for m in enabled_metrics]
    fnames += ["total_score", "max_possible", "percentage"]
    cp = csv_path()
    exists = cp.exists()
    with open(cp, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(row_dict)
    save_raw(raw_dict)
    invalidate_partner_cache()


def delete_partner(partner_name: str) -> None:
    """Remove a partner from both the raw JSON and the scored CSV."""
    # Remove from raw
    rp = raw_path()
    if rp.exists():
        raw = [
            r for r in json.loads(rp.read_text())
            if r.get("partner_name") != partner_name
        ]
        rp.write_text(json.dumps(raw, indent=2))
    # Remove from CSV
    cp = csv_path()
    if cp.exists():
        partners = [p for p in load_partners() if p.get("partner_name") != partner_name]
        if partners:
            with open(cp, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(partners[0].keys()))
                w.writeheader()
                for p in partners:
                    w.writerow(p)
        else:
            cp.unlink()
    invalidate_partner_cache()


def partner_exists(name: str) -> bool:
    """Check whether a partner with the given name already exists."""
    return any(
        p.get("partner_name", "").strip().lower() == name.strip().lower()
        for p in load_partners()
    )


def upsert_partner(row_dict: dict, raw_dict: dict, enabled_metrics: list) -> None:
    """Create or replace a partner (delete-then-append)."""
    pn = row_dict.get("partner_name", "").strip()
    if not pn:
        return
    existing = load_partners()
    if any(p.get("partner_name", "").strip().lower() == pn.lower() for p in existing):
        delete_partner(pn)
    append_partner(row_dict, raw_dict, enabled_metrics)


# ── Tenant config ──────────────────────────────────────────────────────

def load_tenant_config(tid: str | None = None) -> dict:
    """Load the per-tenant configuration dict."""
    tp = tenant_config_path(tid)
    if tp.exists():
        try:
            return json.loads(tp.read_text())
        except Exception:
            pass
    return {}


def save_tenant_config(cfg: dict, tid: str | None = None) -> None:
    """Persist the per-tenant configuration dict."""
    tenant_config_path(tid).write_text(json.dumps(cfg, indent=2))


def max_partners() -> int:
    """Return max partner limit for current tenant (0 = unlimited)."""
    return load_tenant_config().get("max_partners", 0)


def partner_count() -> int:
    """Return current number of partners."""
    return len(load_partners())


# ── Classification config ──────────────────────────────────────────────

def load_q_config() -> dict:
    """Load the quadrant classification config for the active tenant."""
    from utils.scoring import DEFAULT_Q_CONFIG

    cp = class_path()
    if cp.exists():
        try:
            raw = json.loads(cp.read_text())
            return {
                int(k): [(tuple(i) if isinstance(i, list) else i) for i in v]
                for k, v in raw.items()
            }
        except Exception:
            pass
    return DEFAULT_Q_CONFIG.copy()


def save_q_config(config: dict) -> None:
    """Persist the quadrant classification config."""
    class_path().write_text(
        json.dumps({str(k): v for k, v in config.items()}, indent=2)
    )


# ── Break-even config ──────────────────────────────────────────────────

def load_be() -> dict:
    """Load break-even analysis configuration."""
    from utils.scoring import BE_SECTIONS

    p = be_path()
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    # Build default config with all zeros
    cfg: dict = {
        "sections": {},
        "num_partners": 0,
        "support_calls": 0,
        "avg_min_per_call": 20,
    }
    for sec in BE_SECTIONS:
        cfg["sections"][sec["section"]] = {item: 0 for item in sec["items"]}
    return cfg


def save_be(cfg: dict) -> None:
    """Persist the break-even configuration."""
    be_path().write_text(json.dumps(cfg, indent=2))
