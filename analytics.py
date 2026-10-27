"""
analytics.py
============
Pure functions that turn a list of attempts (dictionaries from database.py)
into statistics. No Streamlit, no SQL, so everything is easy to test.

Design rule: never draw strong conclusions from little data. Topic rankings
need MIN_ATTEMPTS_PER_TOPIC attempts in at least two topics; trends need
MIN_ATTEMPTS_FOR_TREND attempts.
"""

import csv
import io

MIN_ATTEMPTS_PER_TOPIC = 3
MIN_ATTEMPTS_FOR_TREND = 4
TREND_THRESHOLD = 3.0  # points of change needed to call it "improving"/"declining"

SCORE_BINS = [
    ("0-19", 0, 19.999),
    ("20-39", 20, 39.999),
    ("40-59", 40, 59.999),
    ("60-79", 60, 79.999),
    ("80-100", 80, 100),
]

CSV_COLUMNS = ["Attempt ID", "Date", "Question ID", "Question", "Topic", "Difficulty", "Score", "Answer"]


def _chronological(attempts):
    return sorted(attempts, key=lambda a: (a["created_at"], a["id"]))


def summary_stats(attempts):
    """Totals shown on the dashboard. Averages are None when there is no data."""
    if not attempts:
        return {"total_attempts": 0, "average_score": None, "best_score": None,
                "sessions": 0, "unique_questions": 0}
    scores = [a["score"] for a in attempts]
    return {
        "total_attempts": len(attempts),
        "average_score": round(sum(scores) / len(scores), 1),
        "best_score": max(scores),
        "sessions": len({a["session_id"] for a in attempts if a.get("session_id")}),
        "unique_questions": len({a["question_id"] for a in attempts}),
    }


def topic_stats(attempts):
    """Average score and attempt count per topic, best average first."""
    grouped = {}
    for a in attempts:
        grouped.setdefault(a["topic"], []).append(a["score"])
    rows = [
        {"topic": topic, "attempts": len(scores), "average": round(sum(scores) / len(scores), 1)}
        for topic, scores in grouped.items()
    ]
    return sorted(rows, key=lambda r: (-r["average"], r["topic"]))


def best_and_weakest_topics(attempts, min_attempts=MIN_ATTEMPTS_PER_TOPIC):
    """
    Only topics with >= min_attempts attempts are compared, and at least two
    such topics are needed. Otherwise we explain why no ranking is shown.
    """
    eligible = [r for r in topic_stats(attempts) if r["attempts"] >= min_attempts]
    if len(eligible) < 2:
        return {
            "best": None, "weakest": None,
            "message": (f"Not enough data yet. Complete at least {min_attempts} attempts in two or more "
                        f"topics to compare them."),
        }
    best, weakest = eligible[0], eligible[-1]
    if best["average"] == weakest["average"]:
        return {"best": None, "weakest": None,
                "message": "Your topic averages are currently equal, so no topic stands out."}
    return {"best": best, "weakest": weakest, "message": ""}


def score_distribution(attempts):
    """Count how many attempts fall into each score range."""
    counts = []
    for label, low, high in SCORE_BINS:
        counts.append({"range": label,
                       "count": sum(1 for a in attempts if low <= a["score"] <= high)})
    return counts


def recent_scores(attempts, n=10):
    """The last n scores in time order (oldest to newest)."""
    ordered = _chronological(attempts)[-n:]
    return [{"created_at": a["created_at"], "score": a["score"]} for a in ordered]


def trend_summary(attempts, window=10, min_attempts=MIN_ATTEMPTS_FOR_TREND):
    """
    Compare the average of the older half with the newer half of the last
    `window` attempts. Small changes are reported as "steady".
    """
    scores = [a["score"] for a in _chronological(attempts)][-window:]
    if len(scores) < min_attempts:
        return {"direction": None, "change": None,
                "message": f"Complete at least {min_attempts} attempts to see a trend."}
    half = len(scores) // 2
    older = sum(scores[:half]) / half
    newer = sum(scores[half:]) / (len(scores) - half)
    change = round(newer - older, 1)
    if change >= TREND_THRESHOLD:
        direction = "improving"
    elif change <= -TREND_THRESHOLD:
        direction = "declining"
    else:
        direction = "steady"
    return {"direction": direction, "change": change,
            "message": f"Newer attempts average {newer:.1f} versus {older:.1f} for older ones ({change:+.1f})."}


def question_improvements(attempts):
    """For every question attempted at least twice: first score, latest score, change."""
    grouped = {}
    for a in _chronological(attempts):
        grouped.setdefault(a["question_id"], []).append(a)
    rows = []
    for qid, items in grouped.items():
        if len(items) < 2:
            continue
        first, latest = items[0]["score"], items[-1]["score"]
        rows.append({
            "question_id": qid,
            "question": items[0]["question_text"],
            "attempts": len(items),
            "first_score": first,
            "latest_score": latest,
            "best_score": max(i["score"] for i in items),
            "change": round(latest - first, 1),
        })
    return sorted(rows, key=lambda r: -r["change"])


def _safe_cell(value):
    """
    Spreadsheet programs run text starting with = + - @ as formulas
    ("CSV injection"). Prefixing a quote makes them display it as text.
    """
    text = "" if value is None else str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def attempts_to_csv(attempts):
    """Return the practice history as CSV text. An empty history gives just the header."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for a in _chronological(attempts):
        writer.writerow([
            a["id"], a["created_at"], a["question_id"], _safe_cell(a["question_text"]),
            a["topic"], a["difficulty"], a["score"], _safe_cell(a["answer"]),
        ])
    return buffer.getvalue()
