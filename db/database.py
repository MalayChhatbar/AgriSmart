import os
import json
import aiosqlite
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

DB_PATH = os.environ.get("AGRISMART_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "agrismart.db"))

_DB_INITIALIZED = False

async def _create_tables(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS farm_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            farmer_name TEXT DEFAULT 'Kisan Mitra',
            farm_location TEXT DEFAULT 'Pune, Maharashtra',
            latitude REAL DEFAULT 18.5204,
            longitude REAL DEFAULT 73.8567,
            primary_crop TEXT DEFAULT 'Tomato',
            soil_type TEXT DEFAULT 'Loamy',
            irrigation_type TEXT DEFAULT 'Drip',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await db.execute("""
        INSERT OR IGNORE INTO farm_profile (id, farmer_name, farm_location, latitude, longitude, primary_crop, soil_type, irrigation_type)
        VALUES (1, 'Kisan Mitra', 'Pune, Maharashtra', 18.5204, 73.8567, 'Tomato', 'Loamy', 'Drip')
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            image_path TEXT,
            plant_name TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            tier INTEGER DEFAULT 1,
            tier_label TEXT DEFAULT 'Confident Diagnosis',
            is_healthy INTEGER DEFAULT 0,
            pathogen TEXT,
            biology TEXT,
            organic_remedies TEXT,
            chemical_remedies TEXT,
            cultural_remedies TEXT,
            environmental_advice TEXT,
            top3 TEXT,
            source_adapter TEXT DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Gracefully add missing columns if upgrading an older database
    for col, col_type in [("top3", "TEXT"), ("source_adapter", "TEXT DEFAULT 'default'"), ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")]:
        try:
            await db.execute(f"ALTER TABLE scans ADD COLUMN {col} {col_type}")
        except Exception:
            pass


    await db.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT DEFAULT 'default',
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            text_hi TEXT,
            tool_calls TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.commit()

@asynccontextmanager
async def get_db_connection():
    global _DB_INITIALIZED
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if not _DB_INITIALIZED:
            await _create_tables(db)
            _DB_INITIALIZED = True
        yield db

async def init_db():
    """Initializes the SQLite database tables if they do not exist."""
    async with get_db_connection() as db:
        pass


        await db.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                image_path TEXT,
                plant_name TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                tier INTEGER DEFAULT 1,
                tier_label TEXT DEFAULT 'Confident Diagnosis',
                is_healthy INTEGER DEFAULT 0,
                pathogen TEXT,
                biology TEXT,
                organic_remedies TEXT,
                chemical_remedies TEXT,
                cultural_remedies TEXT,
                environmental_advice TEXT,
                top3 TEXT,
                source_adapter TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id TEXT PRIMARY KEY,
                session_id TEXT DEFAULT 'default',
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                text_hi TEXT,
                category TEXT DEFAULT 'general',
                tool_calls TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()

# ─── Settings Operations ───
async def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    async with get_db_connection() as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else default

async def set_setting(key: str, value: str):
    async with get_db_connection() as db:
        await db.execute("""
            INSERT INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
        """, (key, value))
        await db.commit()

async def get_all_settings() -> Dict[str, str]:
    async with get_db_connection() as db:
        async with db.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}

async def save_settings_bulk(settings_dict: Dict[str, Any]):
    async with get_db_connection() as db:
        for k, v in settings_dict.items():
            str_val = json.dumps(v) if isinstance(v, (dict, list, bool)) else str(v or "")
            await db.execute("""
                INSERT INTO settings (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
            """, (k, str_val))
        await db.commit()

# ─── Farm Profile Operations ───
async def get_farm_profile() -> Dict[str, Any]:
    async with get_db_connection() as db:
        async with db.execute("SELECT * FROM farm_profile WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return {
                "farmer_name": "Kisan Mitra",
                "farm_location": "Pune, Maharashtra",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "primary_crop": "Tomato",
                "soil_type": "Loamy",
                "irrigation_type": "Drip"
            }

async def update_farm_profile(profile: Dict[str, Any]):
    async with get_db_connection() as db:
        await db.execute("""
            UPDATE farm_profile SET
                farmer_name = COALESCE(?, farmer_name),
                farm_location = COALESCE(?, farm_location),
                latitude = COALESCE(?, latitude),
                longitude = COALESCE(?, longitude),
                primary_crop = COALESCE(?, primary_crop),
                soil_type = COALESCE(?, soil_type),
                irrigation_type = COALESCE(?, irrigation_type),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (
            profile.get("farmer_name"),
            profile.get("farm_location"),
            profile.get("latitude"),
            profile.get("longitude"),
            profile.get("primary_crop"),
            profile.get("soil_type"),
            profile.get("irrigation_type"),
        ))
        await db.commit()

# ─── Scan Operations ───
async def save_scan(scan: Dict[str, Any]):
    async with get_db_connection() as db:
        remedies = scan.get("remedies", {})
        organic = json.dumps(remedies.get("organic", []))
        chemical = json.dumps(remedies.get("chemical", []))
        cultural = json.dumps(remedies.get("cultural", []))
        top3 = json.dumps(scan.get("top3Candidates", scan.get("top3", [])))
        why = scan.get("whyItHappens", {})

        await db.execute("""
            INSERT OR REPLACE INTO scans (
                id, timestamp, image_path, plant_name, disease_name,
                confidence, tier, tier_label, is_healthy, pathogen,
                biology, organic_remedies, chemical_remedies, cultural_remedies,
                environmental_advice, top3, source_adapter
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan.get("id"),
            scan.get("timestamp", datetime.now().isoformat()),
            scan.get("imageUrl", scan.get("image_path", "")),
            scan.get("plantName", scan.get("plant", "Unknown Crop")),
            scan.get("diseaseName", scan.get("disease", "Unknown Condition")),
            float(scan.get("confidence", 0.95)),
            int(scan.get("tier", 1)),
            scan.get("tierLabel", "Confident Diagnosis"),
            1 if scan.get("isHealthy", scan.get("is_healthy", False)) else 0,
            why.get("pathogen", scan.get("pathogen", "")),
            why.get("biology", scan.get("biology", "")),
            organic,
            chemical,
            cultural,
            scan.get("environmentalAdvice", scan.get("environmental_advice", "")),
            top3,
            scan.get("sourceAdapter", scan.get("source_adapter", "default")),
        ))
        await db.commit()

async def get_scans(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    async with get_db_connection() as db:
        async with db.execute("""
            SELECT * FROM scans ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "timestamp": r["timestamp"],
                    "imageUrl": r["image_path"],
                    "plantName": r["plant_name"],
                    "diseaseName": r["disease_name"],
                    "confidence": r["confidence"],
                    "tier": r["tier"],
                    "tierLabel": r["tier_label"],
                    "isHealthy": bool(r["is_healthy"]),
                    "whyItHappens": {
                        "pathogen": r["pathogen"] or "",
                        "biology": r["biology"] or "",
                    },
                    "remedies": {
                        "organic": json.loads(r["organic_remedies"] or "[]"),
                        "chemical": json.loads(r["chemical_remedies"] or "[]"),
                        "cultural": json.loads(r["cultural_remedies"] or "[]"),
                    },
                    "environmentalAdvice": r["environmental_advice"],
                    "top3Candidates": json.loads(r["top3"] or "[]"),
                    "sourceAdapter": r["source_adapter"],
                })
            return results

async def delete_scan(scan_id: str):
    async with get_db_connection() as db:
        await db.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        await db.commit()

async def clear_all_scans():
    async with get_db_connection() as db:
        await db.execute("DELETE FROM scans")
        await db.commit()

# ─── Chat History Operations ───
async def save_chat_message(
    sender: str,
    text: str,
    text_hi: Optional[str] = None,
    category: str = "general",
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    session_id: str = "default",
    msg_id: Optional[str] = None
):
    msg_id = msg_id or f"msg-{int(datetime.now().timestamp() * 1000)}"
    async with get_db_connection() as db:
        await db.execute("""
            INSERT INTO chat_history (id, session_id, sender, text, text_hi, category, tool_calls)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            msg_id,
            session_id,
            sender,
            text,
            text_hi,
            category,
            json.dumps(tool_calls) if tool_calls else None
        ))
        await db.commit()
    return msg_id

async def get_chat_history(session_id: str = "default", limit: int = 30) -> List[Dict[str, Any]]:
    async with get_db_connection() as db:
        async with db.execute("""
            SELECT * FROM chat_history WHERE session_id = ? ORDER BY created_at ASC LIMIT ?
        """, (session_id, limit)) as cursor:
            rows = await cursor.fetchall()
            messages = []
            for r in rows:
                messages.append({
                    "id": r["id"],
                    "sender": r["sender"],
                    "text": r["text"],
                    "textHi": r["text_hi"],
                    "category": r["category"],
                    "toolCalls": json.loads(r["tool_calls"]) if r["tool_calls"] else None,
                    "timestamp": r["created_at"],
                })
            return messages
