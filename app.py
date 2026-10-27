"""
app.py: the Streamlit user interface.

This file only handles DISPLAY and USER INPUT. All scoring lives in evaluator.py,
all SQL in database.py, all statistics in analytics.py.

Streamlit reruns this whole script from top to bottom after every click.
Anything that must survive a rerun is kept in st.session_state.

Run with:  streamlit run app.py
"""

import html
import sqlite3
import uuid

import pandas as pd
import streamlit as st

import analytics
import database
import evaluator
import question_bank

st.set_page_config(page_title="Smart Interview Evaluator", page_icon="🎯", layout="wide")

PAGES = ["Dashboard", "Practice Interview", "Question Library", "Performance Analytics", "Practice History"]
DISCLAIMER = (
    "This score is an estimate from a transparent keyword-based method. It checks which expected concepts "
    "you mentioned; it does not understand meaning, and it is not a measure of your intelligence or of how "
    "a real interview will go."
)

CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 1200px; }
.hero { background: linear-gradient(135deg, #1f3b73 0%, #3b6fd4 100%); color: #ffffff;
        padding: 1.6rem 2rem; border-radius: 14px; margin-bottom: 1.2rem; }
.hero h1 { color: #ffffff; margin: 0 0 .3rem 0; font-size: 1.9rem; }
.hero p { color: #e6edfb; margin: 0; font-size: 1.05rem; }
.metric-card { background: #ffffff; border: 1px solid #dfe5ef; border-radius: 12px;
               padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(20,40,80,.06); }
.metric-label { color: #566176; font-size: .85rem; text-transform: uppercase; letter-spacing: .04em; }
.metric-value { color: #1b2a4a; font-size: 2rem; font-weight: 700; line-height: 1.2; }
.metric-note { color: #6b7587; font-size: .8rem; }
.question-card { background: #f5f8ff; border-left: 5px solid #3b6fd4; padding: 1rem 1.3rem;
                 border-radius: 8px; color: #1b2a4a; font-size: 1.1rem; margin: .5rem 0 1rem 0; }
.badge { display: inline-block; padding: .15rem .65rem; border-radius: 999px; font-size: .78rem;
         font-weight: 600; margin-right: .4rem; background: #e6edfb; color: #1f3b73; }
.score-label { font-size: 1.1rem; font-weight: 600; color: #1f3b73; }
</style>
"""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def metric_card(label, value, note=""):
    """Render one statistic card. html.escape keeps any text safe."""
    st.markdown(
        f"<div class='metric-card'><div class='metric-label'>{html.escape(str(label))}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div>"
        f"<div class='metric-note'>{html.escape(str(note))}</div></div>",
        unsafe_allow_html=True,
    )


def badges(question):
    st.markdown(
        f"<span class='badge'>{html.escape(question['topic'])}</span>"
        f"<span class='badge'>{html.escape(question['difficulty'])}</span>",
        unsafe_allow_html=True,
    )


def show_date(timestamp):
    return str(timestamp).replace("T", " ")


def load_attempts():
    """Read history; show a friendly error instead of crashing if the database is unreadable."""
    try:
        return database.get_all_attempts()
    except sqlite3.Error as error:
        st.error(f"Could not read your practice history: {error}")
        return []


def init_state():
    st.session_state.setdefault("nav_page", "Dashboard")
    st.session_state.setdefault("session_id", uuid.uuid4().hex)  # one id per browser session
    st.session_state.setdefault("drafts", {})                    # unsent answers, per question
    st.session_state.setdefault("last_report", None)


def go_to(page, question_id=None):
    """Button callback: switch page, optionally jumping to a specific question."""
    st.session_state["nav_page"] = page
    if question_id:
        st.session_state["practice_q"] = question_id
        st.session_state["practice_topic"] = "All"
        st.session_state["practice_difficulty"] = "All"
        st.session_state["practice_keyword"] = ""


def reset_filters(prefix):
    st.session_state[f"{prefix}_topic"] = "All"
    st.session_state[f"{prefix}_difficulty"] = "All"
    st.session_state[f"{prefix}_keyword"] = ""


def save_draft(question_id):
    st.session_state["drafts"][question_id] = st.session_state.get(f"answer_{question_id}", "")


def clear_answer(question_id):
    st.session_state["drafts"][question_id] = ""
    st.session_state[f"answer_{question_id}"] = ""
    st.session_state["last_report"] = None


def filter_controls(prefix):
    """Topic / difficulty / keyword filters shared by Practice and Library."""
    col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
    topic = col1.selectbox("Topic", ["All"] + question_bank.TOPICS, key=f"{prefix}_topic")
    difficulty = col2.selectbox("Difficulty", ["All"] + question_bank.DIFFICULTIES, key=f"{prefix}_difficulty")
    keyword = col3.text_input("Search keywords", key=f"{prefix}_keyword",
                              placeholder="e.g. deadlock, index, hash")
    col4.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
    col4.button("Reset", key=f"{prefix}_reset", on_click=reset_filters, args=(prefix,))
    return question_bank.filter_questions(topic=topic, difficulty=difficulty, keyword=keyword)


# ---------------------------------------------------------------------------
# Feedback report
# ---------------------------------------------------------------------------
def render_model_answer(question):
    st.markdown("#### Model answer")
    st.info(question["model_answer"])
    st.markdown("#### Concepts a strong answer covers")
    for concept in question["concepts"]:
        st.markdown(f"- **{concept['name']}**: {concept['hint']}")
    st.markdown("#### Why this answer works")
    st.write(question["why_effective"])
    st.markdown("#### A structure you can reuse for similar questions")
    st.write(question_bank.ANSWER_FRAMEWORKS.get(question["topic"], ""))
    st.caption("Use the model answer to understand the ideas, then explain them in your own words. "
               "Memorized answers sound memorized.")


def render_report(report):
    result = evaluator.EvaluationResult.from_dict(report["result"])
    question = question_bank.get_question_by_id(report["question_id"])

    st.divider()
    st.subheader("Interview Evaluation")
    st.markdown(f"**Question:** {question['question']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Overall score", f"{result.total_score:g}/100", result.label)
    with col2:
        metric_card("Concept coverage", f"{len(result.matched_concepts)}/{result.total_concepts}",
                    "expected concepts found")
    with col3:
        metric_card("Words", result.word_count, "reliable length" if result.reliable else "too short to be reliable")
    st.progress(min(1.0, max(0.0, result.total_score / 100)))

    for warning in result.warnings:
        st.warning(warning)

    st.markdown("#### How the score was calculated")
    for entry in result.breakdown.values():
        left, right = st.columns([1, 3])
        left.markdown(f"**{entry['label']}**  \n{entry['earned']:g} / {entry['max']:g}")
        right.progress(0.0 if not entry["max"] else min(1.0, entry["earned"] / entry["max"]))
        right.caption(entry["detail"])

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Strengths")
        if result.strengths:
            for item in result.strengths:
                st.success(item)
        else:
            st.info("No expected concepts were detected yet.")
    with col_b:
        st.markdown("#### Missing concepts and gaps")
        if result.improvements:
            for item in result.improvements:
                st.warning(item)
        else:
            st.success("Nothing major missing.")

    st.markdown("#### Suggested improvements")
    for item in result.suggestions:
        st.markdown(f"- {item}")
    st.caption(DISCLAIMER)

    reveal_key = f"reveal_{report['attempt_id'] or report['question_id']}"
    if st.checkbox("Show model answer and learning notes", key=reveal_key):
        render_model_answer(question)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_dashboard():
    st.markdown(
        "<div class='hero'><h1>🎯 Smart Interview Answer Evaluator</h1>"
        "<p>Practice technical questions, see exactly which concepts you covered, and track your progress.</p></div>",
        unsafe_allow_html=True,
    )
    attempts = load_attempts()
    stats = analytics.summary_stats(attempts)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Questions attempted", stats["total_attempts"], f"{stats['unique_questions']} unique")
    with col2:
        metric_card("Average score", "-" if stats["average_score"] is None else f"{stats['average_score']:g}", "out of 100")
    with col3:
        metric_card("Practice sessions", stats["sessions"], "one per app visit with attempts")
    with col4:
        metric_card("Best score", "-" if stats["best_score"] is None else f"{stats['best_score']:g}", "personal best")

    st.write("")
    st.button("Start practicing →", type="primary", on_click=go_to, args=("Practice Interview",))

    left, right = st.columns(2)
    with left:
        st.subheader("Recent activity")
        if not attempts:
            st.info("No practice yet. Click **Start practicing** and answer your first question.")
        else:
            rows = [{"Date": show_date(a["created_at"]), "Topic": a["topic"], "Score": a["score"],
                     "Question": a["question_text"]} for a in attempts[:5]]
            st.dataframe(pd.DataFrame(rows), hide_index=True)
    with right:
        st.subheader("Score progress")
        scores = analytics.recent_scores(attempts, n=10)
        if len(scores) < 2:
            st.info("Complete at least two attempts to see your progress chart.")
        else:
            chart = pd.DataFrame({"Score": [s["score"] for s in scores]}, index=range(1, len(scores) + 1))
            chart.index.name = "Attempt (oldest to newest)"
            st.line_chart(chart, y="Score")
            st.caption("Your last 10 attempts in order.")


def page_practice():
    st.title("Practice Interview")
    questions = filter_controls("practice")
    if not questions:
        st.info("No questions match these filters. Try another topic, or press **Reset**.")
        return

    ids = [q["id"] for q in questions]
    if st.session_state.get("practice_q") not in ids:
        st.session_state["practice_q"] = ids[0]
    labels = {q["id"]: f"[{q['difficulty']}] {q['question']}" for q in questions}
    question_id = st.selectbox("Choose a question", ids, key="practice_q", format_func=lambda i: labels[i])
    question = question_bank.get_question_by_id(question_id)

    badges(question)
    st.markdown(f"<div class='question-card'>{html.escape(question['question'])}</div>", unsafe_allow_html=True)

    draft = st.session_state["drafts"].get(question_id, "")
    answer = st.text_area(
        "Your answer", value=draft, key=f"answer_{question_id}", height=220,
        on_change=save_draft, args=(question_id,),
        placeholder="Explain in your own words, as if speaking to an interviewer. Include an example if you can.",
    )
    st.caption(f"{len(answer.split())} words. Tip: aim for roughly 60-120 words covering the key ideas.")

    col_submit, col_clear, _ = st.columns([1, 1, 4])
    submitted = col_submit.button("Submit for evaluation", type="primary")
    col_clear.button("Clear answer", on_click=clear_answer, args=(question_id,))

    if submitted:
        ok, message = evaluator.validate_answer(answer)
        if not ok:
            st.error(message)
        else:
            result = evaluator.evaluate_answer(answer, question)
            attempt_id = None
            try:
                attempt_id = database.save_attempt(question, answer, result, session_id=st.session_state["session_id"])
                st.success("Attempt saved to your practice history.")
            except sqlite3.Error as error:
                st.error(f"Your answer was evaluated but could not be saved: {error}")
            st.session_state["last_report"] = {"question_id": question_id, "attempt_id": attempt_id,
                                               "result": result.to_dict()}

    report = st.session_state.get("last_report")
    if report and report["question_id"] == question_id:
        render_report(report)


def page_library():
    st.title("Question Library")
    questions = filter_controls("library")
    st.caption(f"Showing {len(questions)} of {len(question_bank.get_all_questions())} questions.")
    if not questions:
        st.info("No questions match these filters. Try another topic, or press **Reset**.")
        return

    attempted = {a["question_id"] for a in load_attempts()}
    for q in questions:
        mark = "✅ " if q["id"] in attempted else ""
        with st.expander(f"{mark}{q['question']}"):
            badges(q)
            st.write(f"Concepts to cover: **{len(q['concepts'])}**")
            st.button("Practice this question", key=f"lib_practice_{q['id']}",
                      on_click=go_to, args=("Practice Interview", q["id"]))
            if q["id"] in attempted:
                st.markdown("---")
                render_model_answer(q)
            else:
                st.caption("The model answer unlocks after your first attempt, so it cannot spoil the practice.")


def page_analytics():
    st.title("Performance Analytics")
    attempts = load_attempts()
    if not attempts:
        st.info("Analytics appear after you complete your first practice attempt.")
        return
    stats = analytics.summary_stats(attempts)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Total attempts", stats["total_attempts"])
    with col2:
        metric_card("Average score", f"{stats['average_score']:g}")
    with col3:
        metric_card("Best score", f"{stats['best_score']:g}")

    st.subheader("Topics")
    topics = analytics.best_and_weakest_topics(attempts)
    if topics["best"]:
        a, b = st.columns(2)
        a.success(f"Strongest topic so far: **{topics['best']['topic']}** (average {topics['best']['average']:g})")
        b.warning(f"Needs more practice: **{topics['weakest']['topic']}** (average {topics['weakest']['average']:g})")
    else:
        st.info(topics["message"])
    st.dataframe(pd.DataFrame(analytics.topic_stats(attempts)).rename(
        columns={"topic": "Topic", "attempts": "Attempts", "average": "Average score"}), hide_index=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Score distribution")
        dist = pd.DataFrame(analytics.score_distribution(attempts)).set_index("range")
        st.bar_chart(dist, y="count")
    with right:
        st.subheader("Recent trend")
        trend = analytics.trend_summary(attempts)
        recent = analytics.recent_scores(attempts, n=10)
        if len(recent) >= 2:
            st.line_chart(pd.DataFrame({"Score": [r["score"] for r in recent]}, index=range(1, len(recent) + 1)), y="Score")
        st.caption(trend["message"] if trend["direction"] is None else f"Trend: **{trend['direction']}**. {trend['message']}")

    st.subheader("Improvement on repeated questions")
    improvements = analytics.question_improvements(attempts)
    if improvements:
        table = pd.DataFrame(improvements)[["question", "attempts", "first_score", "latest_score", "best_score", "change"]]
        table.columns = ["Question", "Attempts", "First score", "Latest score", "Best score", "Change"]
        st.dataframe(table, hide_index=True)
    else:
        st.info("Answer the same question at least twice to see how you improve.")

    with st.expander("How are these statistics calculated?"):
        st.markdown(
            f"""
- **Average score**: sum of all attempt scores divided by the number of attempts.
- **Strongest / needs-practice topic**: topics are compared only if they have at least
  {analytics.MIN_ATTEMPTS_PER_TOPIC} attempts, and at least two topics qualify. Fewer attempts is too little evidence.
- **Score distribution**: how many attempts fall in each 20-point range.
- **Trend**: average of the newer half versus the older half of your last 10 attempts. A change under
  {analytics.TREND_THRESHOLD:g} points is called *steady*. Needs at least {analytics.MIN_ATTEMPTS_FOR_TREND} attempts.
- **Improvement**: latest score minus first score for questions attempted at least twice.
- **Sessions**: distinct browser sessions (app visits) that contain at least one saved attempt.
"""
        )


def page_history():
    st.title("Practice History")
    attempts = load_attempts()
    if not attempts:
        st.info("Nothing here yet. Your submitted answers will be listed here.")
        st.button("Download history as CSV", disabled=True, help="No attempts to export yet.")
        return

    try:
        csv_text = analytics.attempts_to_csv(attempts)
        st.download_button("Download history as CSV", data=csv_text.encode("utf-8-sig"),
                           file_name="practice_history.csv", mime="text/csv")
    except Exception as error:  # export should never crash the page
        st.error(f"Could not create the CSV export: {error}")

    table = pd.DataFrame([{"ID": a["id"], "Date": show_date(a["created_at"]), "Topic": a["topic"],
                           "Difficulty": a["difficulty"], "Score": a["score"], "Question": a["question_text"]}
                          for a in attempts])
    st.dataframe(table, hide_index=True)

    st.subheader("Review an attempt")
    by_id = {a["id"]: a for a in attempts}
    chosen = st.selectbox("Choose an attempt", list(by_id), format_func=lambda i: (
        f"#{i} · {show_date(by_id[i]['created_at'])} · {by_id[i]['score']:g}/100 · {by_id[i]['question_text'][:60]}"))
    attempt = by_id[chosen]
    st.markdown(f"**Question:** {attempt['question_text']}")
    st.markdown(f"**Score:** {attempt['score']:g}/100 ({attempt['feedback'].get('label', 'n/a')})")
    st.markdown("**Your answer:**")
    st.text(attempt["answer"])

    feedback = attempt["feedback"]
    if feedback.get("strengths"):
        st.markdown("**Strengths:** " + " ".join(feedback["strengths"]))
    if feedback.get("improvements"):
        st.markdown("**Gaps:** " + " ".join(feedback["improvements"]))

    same_question = [a for a in database.get_attempts_for_question(attempt["question_id"])]
    if len(same_question) > 1:
        st.markdown("**All attempts at this question (oldest to newest):**")
        st.dataframe(pd.DataFrame([{"Attempt": f"#{a['id']}", "Date": show_date(a["created_at"]), "Score": a["score"]}
                                   for a in same_question]), hide_index=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    init_state()
    try:
        database.init_db()
    except (sqlite3.Error, OSError) as error:
        st.error(f"Could not open the local database: {error}")
        st.stop()
    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 🎯 Interview Evaluator")
        st.radio("Navigation", PAGES, key="nav_page")
        st.caption("Runs locally. Your answers stay on this computer in data/practice.db.")

    {
        "Dashboard": page_dashboard,
        "Practice Interview": page_practice,
        "Question Library": page_library,
        "Performance Analytics": page_analytics,
        "Practice History": page_history,
    }[st.session_state["nav_page"]]()


main()
