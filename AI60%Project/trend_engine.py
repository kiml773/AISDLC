from collections import defaultdict
from datetime import datetime, timedelta, timezone

import mood_logic

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def weekly_trend():
    moods = mood_logic.load_moods()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    day_scores = defaultdict(list)
    for entry in moods:
        ts = datetime.fromisoformat(entry["timestamp"])
        # normalise to UTC if naive
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if ts >= cutoff:
            day_name = ts.strftime("%A")
            day_scores[day_name].append(entry["mood_score"])

    return {
        day: (sum(scores) / len(scores)) if scores else 0
        for day, scores in [(d, day_scores[d]) for d in WEEKDAYS]
    }
