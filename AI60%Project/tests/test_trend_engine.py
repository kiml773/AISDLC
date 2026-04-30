import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import mood_logic
import trend_engine

WEEKDAYS = trend_engine.WEEKDAYS


def _make_entry(score, days_ago):
    """Return a mood entry dict with timestamp `days_ago` days in the past."""
    ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {
        "id": f"id-{days_ago}-{score}",
        "mood_score": score,
        "note": "",
        "tags": [],
        "timestamp": ts.isoformat(),
    }


# --- weekly_trend ---

def test_weekly_trend_empty():
    with mock.patch.object(mood_logic, "load_moods", return_value=[]):
        result = trend_engine.weekly_trend()
    assert result == {day: 0 for day in WEEKDAYS}


def test_weekly_trend_single():
    entry = _make_entry(4, days_ago=1)
    day_name = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%A")
    with mock.patch.object(mood_logic, "load_moods", return_value=[entry]):
        result = trend_engine.weekly_trend()
    assert result[day_name] == pytest.approx(4.0)
    # all other days should be zero
    for day in WEEKDAYS:
        if day != day_name:
            assert result[day] == 0


def test_weekly_trend_full_week():
    entries = [_make_entry(score, days_ago=i) for i, score in enumerate(range(1, 8))]
    with mock.patch.object(mood_logic, "load_moods", return_value=entries):
        result = trend_engine.weekly_trend()
    total = sum(result.values())
    assert total == pytest.approx(sum(range(1, 8)))


def test_weekly_trend_duplicate_day():
    """Multiple entries on the same day are averaged correctly."""
    entry1 = _make_entry(2, days_ago=2)
    entry2 = _make_entry(4, days_ago=2)
    day_name = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%A")
    with mock.patch.object(mood_logic, "load_moods", return_value=[entry1, entry2]):
        result = trend_engine.weekly_trend()
    assert result[day_name] == pytest.approx(3.0)


def test_weekly_trend_excludes_old_entries():
    """Entries older than 7 days must not appear in the trend."""
    old_entry = _make_entry(5, days_ago=8)
    day_name = (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%A")
    with mock.patch.object(mood_logic, "load_moods", return_value=[old_entry]):
        result = trend_engine.weekly_trend()
    assert result[day_name] == 0


def test_weekly_trend_returns_all_weekdays():
    with mock.patch.object(mood_logic, "load_moods", return_value=[]):
        result = trend_engine.weekly_trend()
    assert set(result.keys()) == set(WEEKDAYS)
