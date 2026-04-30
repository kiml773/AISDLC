import json

from flask import Flask, redirect, render_template, request, url_for

import mood_logic
import trend_engine

app = Flask(__name__)


@app.route("/")
def index():
    tag = request.args.get("tag", "").strip()
    if tag:
        entries = mood_logic.filter_by_tag(tag)
    else:
        entries = mood_logic.load_moods()
    entries = list(reversed(entries))
    all_tags = sorted({t for e in mood_logic.load_moods() for t in e.get("tags", [])})
    return render_template("index.html", entries=entries, active_tag=tag, all_tags=all_tags)


@app.route("/mood", methods=["POST"])
def create_mood():
    try:
        score = int(request.form.get("mood_score", 0))
    except ValueError:
        score = 0
    note = request.form.get("note", "")
    raw_tags = request.form.get("tags", "")
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    try:
        mood_logic.add_entry(score, note, tags)
    except ValueError as exc:
        entries = list(reversed(mood_logic.load_moods()))
        all_tags = sorted({t for e in mood_logic.load_moods() for t in e.get("tags", [])})
        return render_template("index.html", entries=entries, error=str(exc), active_tag="", all_tags=all_tags), 400
    return redirect(url_for("index"))


@app.route("/mood/<entry_id>/delete", methods=["POST"])
def delete_mood(entry_id):
    try:
        mood_logic.delete_entry(entry_id)
    except KeyError:
        pass
    return redirect(url_for("index"))


@app.route("/mood/<entry_id>/edit", methods=["GET"])
def edit_mood(entry_id):
    moods = mood_logic.load_moods()
    entry = next((e for e in moods if e["id"] == entry_id), None)
    if entry is None:
        return redirect(url_for("index"))
    return render_template("edit.html", entry=entry)


@app.route("/mood/<entry_id>/update", methods=["POST"])
def update_mood(entry_id):
    try:
        score = int(request.form.get("mood_score", 0))
    except ValueError:
        score = 0
    note = request.form.get("note", "")
    raw_tags = request.form.get("tags", "")
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    try:
        mood_logic.update_entry(entry_id, score, note, tags)
    except (ValueError, KeyError) as exc:
        moods = mood_logic.load_moods()
        entry = next((e for e in moods if e["id"] == entry_id), None)
        return render_template("edit.html", entry=entry, error=str(exc)), 400
    return redirect(url_for("index"))


@app.route("/chart")
def chart():
    trend = trend_engine.weekly_trend()
    return render_template("chart.html", trend_json=json.dumps(trend))


@app.route("/api/trend")
def api_trend():
    trend = trend_engine.weekly_trend()
    fmt = request.args.get("format", "json")
    if fmt == "ascii":
        lines = ["Weekly Mood Trend", "=" * 36]
        for day, avg in trend.items():
            bar = "#" * round(avg * 4)
            lines.append(f"{day:<12} {avg:.2f} |{bar}")
        return "\n".join(lines), 200, {"Content-Type": "text/plain; charset=utf-8"}
    return json.dumps(trend), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(debug=True)
