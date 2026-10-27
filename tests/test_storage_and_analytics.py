"""Tests for database.py, analytics.py (including CSV export) and question_bank.py."""

import csv
import io
import os
import tempfile
import unittest

import analytics
import database
import evaluator
import question_bank

QUESTION = question_bank.get_question_by_id("PY-01")
OTHER_QUESTION = question_bank.get_question_by_id("SQL-01")


def make_attempt(attempt_id, score, topic="Python", qid="PY-01", created="2026-01-01T10:00:00",
                 session="s1", answer="an answer", text="A question?"):
    """Build an attempt dictionary shaped like the ones database.py returns."""
    return {"id": attempt_id, "question_id": qid, "question_text": text, "topic": topic,
            "difficulty": "Beginner", "answer": answer, "score": score, "session_id": session,
            "created_at": created, "feedback": {}}


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "nested", "test.db")  # nested folder is created for us
        database.init_db(self.db)
        self.result = evaluator.evaluate_answer(QUESTION["model_answer"], QUESTION)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_database_returns_empty_list(self):
        self.assertEqual(database.get_all_attempts(self.db), [])
        self.assertEqual(database.count_attempts(self.db), 0)

    def test_init_db_is_safe_to_call_twice(self):
        database.init_db(self.db)
        database.init_db(self.db)

    def test_save_and_retrieve_attempt(self):
        attempt_id = database.save_attempt(QUESTION, "my answer", self.result, session_id="abc", db_path=self.db)
        saved = database.get_attempt(attempt_id, self.db)
        self.assertEqual(saved["question_id"], "PY-01")
        self.assertEqual(saved["topic"], QUESTION["topic"])
        self.assertEqual(saved["difficulty"], QUESTION["difficulty"])
        self.assertEqual(saved["answer"], "my answer")
        self.assertEqual(saved["score"], self.result.total_score)
        self.assertEqual(saved["session_id"], "abc")
        self.assertEqual(saved["feedback"]["label"], self.result.label)
        self.assertTrue(saved["created_at"])

    def test_missing_attempt_returns_none(self):
        self.assertIsNone(database.get_attempt(9999, self.db))

    def test_repeated_attempts_are_all_kept(self):
        first = database.save_attempt(QUESTION, "first try", self.result, db_path=self.db,
                                      created_at="2026-01-01T10:00:00")
        second = database.save_attempt(QUESTION, "second try", self.result, db_path=self.db,
                                       created_at="2026-01-02T10:00:00")
        self.assertNotEqual(first, second)
        history = database.get_attempts_for_question("PY-01", self.db)
        self.assertEqual([a["answer"] for a in history], ["first try", "second try"])  # oldest first
        self.assertEqual(database.count_attempts(self.db), 2)

    def test_get_all_attempts_is_newest_first(self):
        database.save_attempt(QUESTION, "old", self.result, db_path=self.db, created_at="2026-01-01T10:00:00")
        database.save_attempt(OTHER_QUESTION, "new", self.result, db_path=self.db, created_at="2026-02-01T10:00:00")
        self.assertEqual([a["answer"] for a in database.get_all_attempts(self.db)], ["new", "old"])

    def test_sql_injection_text_is_stored_literally(self):
        nasty = "x'); DROP TABLE attempts; --"
        database.save_attempt(QUESTION, nasty, self.result, db_path=self.db)
        self.assertEqual(database.get_all_attempts(self.db)[0]["answer"], nasty)
        self.assertEqual(database.count_attempts(self.db), 1)

    def test_unicode_answer_round_trip(self):
        text = "Résumé: naïve café — 日本語"
        attempt_id = database.save_attempt(QUESTION, text, self.result, db_path=self.db)
        self.assertEqual(database.get_attempt(attempt_id, self.db)["answer"], text)


class TestAnalytics(unittest.TestCase):
    def test_summary_of_empty_history(self):
        stats = analytics.summary_stats([])
        self.assertEqual(stats["total_attempts"], 0)
        self.assertIsNone(stats["average_score"])
        self.assertEqual(stats["sessions"], 0)

    def test_summary_counts_sessions_and_average(self):
        attempts = [make_attempt(1, 60, session="a"), make_attempt(2, 80, session="a"),
                    make_attempt(3, 100, session="b"), make_attempt(4, 40, session=None)]
        stats = analytics.summary_stats(attempts)
        self.assertEqual(stats["total_attempts"], 4)
        self.assertEqual(stats["average_score"], 70.0)
        self.assertEqual(stats["best_score"], 100)
        self.assertEqual(stats["sessions"], 2)

    def test_topic_ranking_needs_enough_data(self):
        one_each = [make_attempt(1, 90, topic="Python"), make_attempt(2, 20, topic="SQL and Databases")]
        result = analytics.best_and_weakest_topics(one_each)
        self.assertIsNone(result["best"])
        self.assertIsNone(result["weakest"])
        self.assertIn("Not enough data", result["message"])

    def test_topic_ranking_with_enough_data(self):
        attempts = [make_attempt(i, 90, topic="Python") for i in range(1, 4)]
        attempts += [make_attempt(i, 40, topic="SQL and Databases") for i in range(4, 7)]
        result = analytics.best_and_weakest_topics(attempts)
        self.assertEqual(result["best"]["topic"], "Python")
        self.assertEqual(result["weakest"]["topic"], "SQL and Databases")

    def test_topic_ranking_ties_do_not_pick_a_loser(self):
        attempts = [make_attempt(i, 70, topic="Python") for i in range(1, 4)]
        attempts += [make_attempt(i, 70, topic="SQL and Databases") for i in range(4, 7)]
        self.assertIsNone(analytics.best_and_weakest_topics(attempts)["weakest"])

    def test_score_distribution_boundaries(self):
        scores = [0, 19.9, 20, 39.9, 40, 59.9, 60, 79.9, 80, 100]
        attempts = [make_attempt(i, s) for i, s in enumerate(scores, start=1)]
        counts = {row["range"]: row["count"] for row in analytics.score_distribution(attempts)}
        self.assertEqual(counts, {"0-19": 2, "20-39": 2, "40-59": 2, "60-79": 2, "80-100": 2})

    def test_score_distribution_of_empty_history(self):
        self.assertTrue(all(row["count"] == 0 for row in analytics.score_distribution([])))

    def test_recent_scores_are_chronological_and_limited(self):
        attempts = [make_attempt(i, i * 10, created=f"2026-01-{i:02d}T10:00:00") for i in range(1, 8)]
        recent = analytics.recent_scores(list(reversed(attempts)), n=3)
        self.assertEqual([r["score"] for r in recent], [50, 60, 70])

    def test_trend_needs_enough_attempts(self):
        attempts = [make_attempt(i, 50) for i in range(1, 3)]
        self.assertIsNone(analytics.trend_summary(attempts)["direction"])

    def test_trend_improving_declining_steady(self):
        def build(scores):
            return [make_attempt(i, s, created=f"2026-01-{i:02d}T10:00:00") for i, s in enumerate(scores, start=1)]
        self.assertEqual(analytics.trend_summary(build([40, 40, 60, 60]))["direction"], "improving")
        self.assertEqual(analytics.trend_summary(build([80, 80, 60, 60]))["direction"], "declining")
        self.assertEqual(analytics.trend_summary(build([60, 61, 60, 61]))["direction"], "steady")

    def test_question_improvement_only_for_repeated_questions(self):
        attempts = [
            make_attempt(1, 40, qid="PY-01", created="2026-01-01T10:00:00"),
            make_attempt(2, 75, qid="PY-01", created="2026-01-02T10:00:00"),
            make_attempt(3, 90, qid="SQL-01", created="2026-01-03T10:00:00"),
        ]
        rows = analytics.question_improvements(attempts)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question_id"], "PY-01")
        self.assertEqual(rows[0]["change"], 35)
        self.assertEqual(rows[0]["first_score"], 40)
        self.assertEqual(rows[0]["latest_score"], 75)


class TestCsvExport(unittest.TestCase):
    def test_empty_history_gives_header_only(self):
        rows = list(csv.reader(io.StringIO(analytics.attempts_to_csv([]))))
        self.assertEqual(rows, [analytics.CSV_COLUMNS])

    def test_rows_contain_expected_fields(self):
        attempts = [make_attempt(1, 77.5, text="What is X?", answer="X is a thing, really.")]
        rows = list(csv.reader(io.StringIO(analytics.attempts_to_csv(attempts))))
        self.assertEqual(len(rows), 2)
        row = dict(zip(rows[0], rows[1]))
        self.assertEqual(row["Question"], "What is X?")
        self.assertEqual(row["Topic"], "Python")
        self.assertEqual(row["Score"], "77.5")
        self.assertEqual(row["Answer"], "X is a thing, really.")  # comma survived quoting

    def test_formula_injection_is_neutralised(self):
        attempts = [make_attempt(1, 50, answer="=HYPERLINK(\"http://evil\")", text="+cmd")]
        rows = list(csv.reader(io.StringIO(analytics.attempts_to_csv(attempts))))
        row = dict(zip(rows[0], rows[1]))
        self.assertTrue(row["Answer"].startswith("'="))
        self.assertTrue(row["Question"].startswith("'+"))

    def test_multiline_answers_round_trip(self):
        attempts = [make_attempt(1, 50, answer="line one\nline two")]
        rows = list(csv.reader(io.StringIO(analytics.attempts_to_csv(attempts))))
        self.assertEqual(rows[1][-1], "line one\nline two")


class TestQuestionBank(unittest.TestCase):
    def test_bank_is_well_formed(self):
        self.assertEqual(question_bank.validate_question_bank(), [])

    def test_size_and_coverage(self):
        questions = question_bank.get_all_questions()
        self.assertGreaterEqual(len(questions), 30)
        self.assertLessEqual(len(questions), 40)
        self.assertEqual({q["topic"] for q in questions}, set(question_bank.TOPICS))
        self.assertEqual({q["difficulty"] for q in questions}, set(question_bank.DIFFICULTIES))

    def test_validation_catches_problems(self):
        broken = [{"id": "X", "topic": "Nope", "difficulty": "Beginner", "question": "q",
                   "concepts": [], "model_answer": "m", "why_effective": "w"}]
        self.assertTrue(question_bank.validate_question_bank(broken))

    def test_filter_by_topic_and_difficulty(self):
        results = question_bank.filter_questions(topic="Python", difficulty="Beginner")
        self.assertTrue(results)
        self.assertTrue(all(q["topic"] == "Python" and q["difficulty"] == "Beginner" for q in results))

    def test_filter_all_means_no_filter(self):
        self.assertEqual(len(question_bank.filter_questions("All", "All", "")),
                         len(question_bank.get_all_questions()))

    def test_keyword_search_is_case_insensitive_and_can_return_nothing(self):
        self.assertTrue(question_bank.filter_questions(keyword="DEADLOCK"))
        self.assertEqual(question_bank.filter_questions(keyword="zzzz-no-such-thing"), [])

    def test_keyword_search_does_not_reveal_model_answers(self):
        # 'pile of plates' appears only inside the DSA-01 model answer, never in question text or concept names.
        self.assertEqual(question_bank.filter_questions(keyword="pile of plates"), [])

    def test_get_question_by_id(self):
        self.assertEqual(question_bank.get_question_by_id("PY-01")["topic"], "Python")
        self.assertIsNone(question_bank.get_question_by_id("NOPE"))


if __name__ == "__main__":
    unittest.main()
