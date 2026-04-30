# Mood Journal with Insights

A locally-hosted web application for logging mood entries, categorising them with tags, and visualising weekly emotional trends. Built with Python/Flask, HTML/JS, and local JSON storage. No external APIs.

**COMP8066 — AI-Powered SDLC | Project 2 | Option E**

---

## Features

- Create, read, update, and delete mood entries (score 1–5, optional note, tags)
- Filter entries by tag
- Weekly mood trend chart (Chart.js bar chart)
- ASCII trend output available at `/api/trend?format=ascii`
- All data stored locally in `data/moods.json` — no accounts, no external services

---

## Project Structure

```
AI60%Project/
├── app.py              # Flask application and route definitions
├── mood_logic.py       # CRUD functions: add, delete, update, filter, load, save
├── trend_engine.py     # weekly_trend() — groups entries by weekday, averages scores
├── requirements.txt    # Python dependencies
├── data/
│   └── moods.json      # Persistent local storage (auto-created on first run)
├── templates/
│   ├── index.html      # Entry list + add form
│   ├── chart.html      # Weekly trend bar chart
│   └── edit.html       # Edit existing entry
└── tests/
    ├── test_mood_logic.py    # Unit tests for CRUD and validation logic
    └── test_trend_engine.py  # Unit tests for weekly trend calculations
```

---

## Requirements

- Python 3.11 or later
- pip

---

## Setup and Run

```bash
# 1. Clone the repository
git clone https://github.com/kiml773/AISDLC
cd AISDLC/AI60%Project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

> **Note:** This uses the Flask development server, which is not production-safe. For local use only.

---

## Running Tests

```bash
pytest tests/
```

All tests use pytest with no external mocking libraries. The test suite covers:

- `add_entry()` — valid input, invalid score range, invalid score type
- `delete_entry()` — existing ID, non-existent ID (KeyError)
- `filter_by_tag()` — tag match
- `weekly_trend()` — empty input, single entry, full week, duplicate entries on same day
- Integration: create → save → reload from JSON

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Entry list, optional `?tag=` filter |
| POST | `/mood` | Create a new mood entry |
| GET | `/mood/<id>/edit` | Edit form for an entry |
| POST | `/mood/<id>/update` | Update an existing entry |
| POST | `/mood/<id>/delete` | Delete an entry |
| GET | `/chart` | Weekly trend bar chart |
| GET | `/api/trend` | Trend data as JSON or `?format=ascii` |

---

## Data Storage

Entries are stored in `data/moods.json` as a JSON array. Each entry has the following shape:

```json
{
  "id": "uuid4-string",
  "mood_score": 4,
  "note": "Felt productive today",
  "tags": ["work", "focus"],
  "timestamp": "2025-04-30T10:00:00+00:00"
}
```

The file is created automatically if it does not exist. If it contains malformed JSON, the app logs a warning and starts with an empty list rather than crashing.

---

## Notes

- Mood scores must be integers between 1 and 5 (inclusive)
- Tags are optional; an empty tag list is valid
- The app has no authentication — intended for single-user local use only
- The JSON file is stored in plaintext; do not store sensitive data on shared machines
