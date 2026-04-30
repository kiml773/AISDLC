import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# allow importing from project root
sys.path.insert(0, str(Path(__file__).parent.parent))
import mood_logic


@pytest.fixture(autouse=True)
def temp_data_file(tmp_path, monkeypatch):
    """Redirect DATA_FILE to a temp path for every test."""
    tmp_file = tmp_path / "moods.json"
    monkeypatch.setattr(mood_logic, "DATA_FILE", tmp_file)
    yield tmp_file


# --- add_entry ---

def test_add_entry_valid():
    entry = mood_logic.add_entry(4, "Feeling good", ["work", "exercise"])
    moods = mood_logic.load_moods()
    assert any(e["id"] == entry["id"] for e in moods)
    assert entry["mood_score"] == 4
    assert "work" in entry["tags"]


def test_add_entry_invalid_score_high():
    with pytest.raises(ValueError):
        mood_logic.add_entry(6, "Too high", [])


def test_add_entry_invalid_score_low():
    with pytest.raises(ValueError):
        mood_logic.add_entry(0, "Too low", [])


def test_add_entry_invalid_score_type():
    with pytest.raises(ValueError):
        mood_logic.add_entry("five", "Not int", [])


def test_add_entry_tags_not_list():
    with pytest.raises(ValueError):
        mood_logic.add_entry(3, "Note", "work")


def test_add_entry_empty_note():
    entry = mood_logic.add_entry(3, "", [])
    assert entry["note"] == ""


# --- delete_entry ---

def test_delete_entry_exists():
    entry = mood_logic.add_entry(3, "To delete", ["test"])
    mood_logic.delete_entry(entry["id"])
    moods = mood_logic.load_moods()
    assert not any(e["id"] == entry["id"] for e in moods)


def test_delete_entry_not_found():
    with pytest.raises(KeyError):
        mood_logic.delete_entry("nonexistent-id")


# --- update_entry ---

def test_update_entry_valid():
    entry = mood_logic.add_entry(2, "Original", ["old"])
    mood_logic.update_entry(entry["id"], 5, "Updated", ["new"])
    moods = mood_logic.load_moods()
    updated = next(e for e in moods if e["id"] == entry["id"])
    assert updated["mood_score"] == 5
    assert updated["note"] == "Updated"
    assert updated["tags"] == ["new"]


def test_update_entry_not_found():
    with pytest.raises(KeyError):
        mood_logic.update_entry("bad-id", 3, "Note", [])


def test_update_entry_invalid_score():
    entry = mood_logic.add_entry(3, "Note", [])
    with pytest.raises(ValueError):
        mood_logic.update_entry(entry["id"], 10, "Note", [])


# --- filter_by_tag ---

def test_filter_by_tag():
    mood_logic.add_entry(4, "Entry 1", ["work", "coffee"])
    mood_logic.add_entry(2, "Entry 2", ["sleep"])
    mood_logic.add_entry(5, "Entry 3", ["work"])
    result = mood_logic.filter_by_tag("work")
    assert len(result) == 2
    assert all("work" in e["tags"] for e in result)


def test_filter_by_tag_case_insensitive():
    mood_logic.add_entry(3, "Entry", ["Work"])
    result = mood_logic.filter_by_tag("work")
    assert len(result) == 1


def test_filter_by_tag_no_match():
    mood_logic.add_entry(3, "Entry", ["sleep"])
    result = mood_logic.filter_by_tag("gym")
    assert result == []


# --- load_moods / save_moods ---

def test_create_save_reload(tmp_path, monkeypatch):
    """Integration: add entry, save, reload, verify persistence."""
    tmp_file = tmp_path / "integration.json"
    monkeypatch.setattr(mood_logic, "DATA_FILE", tmp_file)

    entry = mood_logic.add_entry(5, "Integration test", ["integration"])
    mood_logic.save_moods(mood_logic.load_moods())
    reloaded = mood_logic.load_moods()

    match = next((e for e in reloaded if e["id"] == entry["id"]), None)
    assert match is not None
    assert match["mood_score"] == 5
    assert match["note"] == "Integration test"
    assert "integration" in match["tags"]


def test_load_moods_migration_adds_timestamp(tmp_path, monkeypatch):
    """load_moods() injects timestamp into legacy entries that lack one."""
    tmp_file = tmp_path / "legacy.json"
    legacy = [{"id": "abc", "mood_score": 3, "note": "", "tags": []}]
    tmp_file.write_text(json.dumps(legacy))
    monkeypatch.setattr(mood_logic, "DATA_FILE", tmp_file)

    moods = mood_logic.load_moods()
    assert "timestamp" in moods[0]


def test_load_moods_empty_file(tmp_path, monkeypatch):
    tmp_file = tmp_path / "empty.json"
    tmp_file.write_text("")
    monkeypatch.setattr(mood_logic, "DATA_FILE", tmp_file)
    assert mood_logic.load_moods() == []
