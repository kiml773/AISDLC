import json
import uuid
from datetime import datetime, date as date_type, timezone
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "moods.json"


def load_moods():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            entries = json.load(f)
        except json.JSONDecodeError:
            return []
    # migration: inject default timestamp if missing
    for entry in entries:
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    return entries


def save_moods(moods):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(moods, f, indent=2, ensure_ascii=False)


def _parse_timestamp(date_str):
    """Return an ISO timestamp string for a given YYYY-MM-DD string, or now if None."""
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return d.isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()


def filter_by_date(date_str):
    """Return entries whose timestamp falls on the given YYYY-MM-DD date."""
    return [e for e in load_moods() if e.get("timestamp", "")[:10] == date_str]


def add_entry(score, note, tags, entry_date=None):
    if not isinstance(score, int) or not (1 <= score <= 5):
        raise ValueError("mood_score must be an integer between 1 and 5")
    if not isinstance(tags, list):
        raise ValueError("tags must be a list")

    entry = {
        "id": str(uuid.uuid4()),
        "mood_score": score,
        "note": note or "",
        "tags": [t.strip() for t in tags if t.strip()],
        "timestamp": _parse_timestamp(entry_date),
    }
    moods = load_moods()
    moods.append(entry)
    save_moods(moods)
    return entry


def delete_entry(entry_id):
    moods = load_moods()
    original_len = len(moods)
    moods = [e for e in moods if e["id"] != entry_id]
    if len(moods) == original_len:
        raise KeyError(f"No entry with id {entry_id}")
    save_moods(moods)


def update_entry(entry_id, score, note, tags, entry_date=None):
    if not isinstance(score, int) or not (1 <= score <= 5):
        raise ValueError("mood_score must be an integer between 1 and 5")
    if not isinstance(tags, list):
        raise ValueError("tags must be a list")

    moods = load_moods()
    for entry in moods:
        if entry["id"] == entry_id:
            entry["mood_score"] = score
            entry["note"] = note or ""
            entry["tags"] = [t.strip() for t in tags if t.strip()]
            if entry_date:
                entry["timestamp"] = _parse_timestamp(entry_date)
            save_moods(moods)
            return entry
    raise KeyError(f"No entry with id {entry_id}")


def filter_by_tag(tag):
    tag = tag.strip().lower()
    return [e for e in load_moods() if tag in [t.lower() for t in e.get("tags", [])]]
