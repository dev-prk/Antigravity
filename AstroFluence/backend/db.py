"""SQLite Persistent Vault for Profiles, Stored Discipline Readings, Atomic Claims, and Chat History."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.engine.ontology import ProfileInput
from backend.engine.synthesizer import compute_full_profile_readings

DB_PATH = os.path.join(os.path.dirname(__file__), "astrofluence.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            profile_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role_tag TEXT NOT NULL DEFAULT 'Personal Vault',
            bundle_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            msg_id TEXT PRIMARY KEY,
            profile_id TEXT NOT NULL,
            surface TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    seed_default_profiles()


def save_profile_bundle(profile_id: str, role_tag: str, bundle: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    name = bundle["profile_input"]["name"]
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT created_at FROM profiles WHERE profile_id = ?", (profile_id,))
    row = cur.fetchone()
    created_at = row["created_at"] if row else now

    cur.execute(
        """
        INSERT OR REPLACE INTO profiles (profile_id, name, role_tag, bundle_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (profile_id, name, role_tag, json.dumps(bundle), created_at, now),
    )
    conn.commit()
    conn.close()
    return bundle


def get_profile_bundle(profile_id: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    bundle = json.loads(row["bundle_json"])
    bundle["role_tag"] = row["role_tag"]
    bundle["updated_at"] = row["updated_at"]
    return bundle


def list_profiles() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT profile_id, name, role_tag, bundle_json, updated_at FROM profiles ORDER BY created_at ASC")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        bundle = json.loads(r["bundle_json"])
        audit = bundle.get("cross_validation_audit", {})
        inp = bundle.get("profile_input", {})
        out.append(
            {
                "profile_id": r["profile_id"],
                "name": r["name"],
                "role_tag": r["role_tag"],
                "birth_date": inp.get("birth_date"),
                "birth_city": inp.get("birth_city"),
                "total_claims": audit.get("total_claims_analyzed", 0),
                "verified_patterns_count": len(audit.get("verified_core_patterns", [])),
                "active_disciplines": audit.get("active_disciplines", []),
                "updated_at": r["updated_at"],
            }
        )
    return out


def append_chat_message(
    msg_id: str,
    profile_id: str,
    surface: str,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_messages (msg_id, profile_id, surface, role, content, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            msg_id,
            profile_id,
            surface,
            role,
            content,
            json.dumps(metadata or {}),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_chat_history(profile_id: str, surface: str = "workbench") -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM chat_messages WHERE profile_id = ? AND surface = ? ORDER BY created_at ASC",
        (profile_id, surface),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "msg_id": r["msg_id"],
            "profile_id": r["profile_id"],
            "surface": r["surface"],
            "role": r["role"],
            "content": r["content"],
            "metadata": json.loads(r["metadata_json"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def seed_default_profiles() -> None:
    if get_profile_bundle("prf_devesh_prime"):
        return

    # 1. Devesh Prime Vault Profile (Demonstrating the exact Palmistry + Numerology -> Astrology + Vastu Triangulation)
    devesh_inp = ProfileInput(
        name="Devesh Prakash",
        birth_date="1996-08-15",
        birth_time="10:30",
        timezone_offset=5.5,
        birth_city="New Delhi, India",
        latitude=28.6139,
        longitude=77.2090,
        current_city="Bengaluru, India",
        palmistry_data={
            "hand_element": "Air-Fire (Long fingers, active Mercury & Moon mounts)",
            "head_line": "forked_to_moon",
            "fate_line": "deep_to_saturn_and_jupiter",
            "dominant_mounts": "mercury_and_moon",
            "heart_line": "Deep curve ending beneath Mount of Jupiter (idealistic loyalty)",
            "raw_notes": "Deep forked Head Line sloping toward Mount of Moon + Mystic Cross in Quadrangle; cautious Saturn fate line balanced by strong Jupiter branch.",
        },
        vastu_data={
            "entrance_direction": "North-East",
            "workspace_zone": "North-West",
            "desk_facing": "North",
            "sleeping_head_direction": "South",
            "clutter_zones": [],
            "raw_notes": "North-West studio aligned for creative velocity; solid South-West earth wall behind work chair.",
        },
        oracle_data={
            "tarot_card": "The Magician (I)",
            "iching_hexagram": "Hexagram 50 — Ding (The Cauldron / Alchemical Vessel)",
        },
        custom_notes=[
            {
                "discipline_name": "Graphology (Handwriting Analysis)",
                "text": "High upper-zone extensions with connected fluid strokes and forward slant indicate creative communication and rapid architectural synthesis.",
                "trait_tag": "creative_communication",
                "domain": "career_wealth",
            },
            {
                "discipline_name": "Physiognomy (Samudrika Face Reading)",
                "text": "Broad high forehead with pronounced brow ridge indicates analytical precision and autonomous executive leadership.",
                "trait_tag": "executive_leadership",
                "domain": "career_wealth",
            },
        ],
    )
    bundle_1 = compute_full_profile_readings("prf_devesh_prime", devesh_inp)
    save_profile_bundle("prf_devesh_prime", "Founder Personal Vault", bundle_1)

    # 2. Sample Client Profile for Website Chatbot Testing
    aria_inp = ProfileInput(
        name="Aria Sharma",
        birth_date="1994-11-03",
        birth_time="18:15",
        timezone_offset=5.5,
        birth_city="Mumbai, India",
        latitude=19.0760,
        longitude=72.8777,
        current_city="London, UK",
        palmistry_data={
            "hand_element": "Water-Earth",
            "head_line": "straight_long",
            "fate_line": "self_made_from_head",
            "dominant_mounts": "intuition_crescent",
        },
        vastu_data={
            "entrance_direction": "East",
            "workspace_zone": "West",
            "desk_facing": "East",
            "sleeping_head_direction": "South",
        },
        oracle_data={
            "tarot_card": "Wheel of Fortune (X)",
            "iching_hexagram": "Hexagram 14 — Da You (Possession in Great Measure)",
        },
        custom_notes=[],
    )
    bundle_2 = compute_full_profile_readings("prf_client_aria", aria_inp)
    save_profile_bundle("prf_client_aria", "Website Chatbot Visitor", bundle_2)
