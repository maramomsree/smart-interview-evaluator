"""Tests for evaluator.py (run from the project root: python -m unittest discover -v)."""

import random
import string
import unittest

import evaluator
import question_bank

# A small, fixed question so these tests do not depend on the real question bank.
SAMPLE_QUESTION = {
    "id": "TEST-01",
    "topic": "Python",
    "difficulty": "Beginner",
    "question": "What is the difference between a list and a tuple?",
    "concepts": [
        {"name": "Mutability", "hint": "Explain mutability.",
         "keywords": ["mutable", "immutable", "cannot be changed"]},
        {"name": "Performance", "hint": "Mention speed and memory.",
         "keywords": ["faster", "memory"]},
        {"name": "Sorting", "hint": "Mention sorted data.",
         "keywords": ["sorted"]},
    ],
    "model_answer": "unused",
    "why_effective": "unused",
}

GOOD_ANSWER = (
    "A list is mutable, so you can change it after creation, while a tuple is immutable and cannot be "
    "changed. Tuples are usually faster and use less memory. For example, I store coordinates in a tuple."
)


class TestNormalizationAndMatching(unittest.TestCase):
    def test_normalize_lowercases_and_strips_punctuation(self):
        self.assertEqual(evaluator.normalize_text("  Hello,   WORLD!!  "), "hello world")

    def test_normalize_hyphens_match_spaces(self):
        self.assertEqual(evaluator.normalize_text("First-In-First-Out"),
                         evaluator.normalize_text("first in first out"))

    def test_normalize_keeps_plus_and_sharp(self):
        self.assertEqual(evaluator.normalize_text("C++ and C#"), "c++ and c#")

    def test_case_and_punctuation_do_not_matter(self):
        result = evaluator.evaluate_answer("MUTABLE!!! (really) " + "word " * 20, SAMPLE_QUESTION)
        self.assertIn("Mutability", result.matched_concepts)

    def test_whole_word_matching_prevents_false_positives(self):
        # 'sorted' must not match inside 'unsorted'
        self.assertFalse(evaluator.contains_phrase("the data is unsorted", "sorted"))
        self.assertTrue(evaluator.contains_phrase("the data is sorted", "sorted"))

    def test_simple_plural_still_matches(self):
        self.assertTrue(evaluator.contains_phrase("many hashes exist", "hash"))

    def test_empty_keyword_never_matches(self):
        self.assertFalse(evaluator.contains_phrase("anything", "!!!"))


class TestEvaluation(unittest.TestCase):
    def test_identifies_matched_and_missing_concepts(self):
        result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        self.assertEqual(result.matched_concepts, ["Mutability", "Performance"])
        self.assertEqual([m["name"] for m in result.missing_concepts], ["Sorting"])
        self.assertEqual(result.total_concepts, 3)

    def test_empty_answer_raises(self):
        for bad in ("", "   ", "\n\t", None):
            with self.assertRaises(ValueError):
                evaluator.evaluate_answer(bad, SAMPLE_QUESTION)

    def test_validate_answer_messages(self):
        self.assertFalse(evaluator.validate_answer("")[0])
        self.assertTrue(evaluator.validate_answer("hello")[0])
        self.assertFalse(evaluator.validate_answer("x" * (evaluator.MAX_ANSWER_CHARS + 1))[0])

    def test_very_short_answer_is_flagged_and_capped(self):
        result = evaluator.evaluate_answer("mutable faster memory sorted", SAMPLE_QUESTION)
        self.assertFalse(result.reliable)
        self.assertLessEqual(result.total_score, evaluator.SHORT_ANSWER_SCORE_CAP)
        self.assertTrue(any("cannot be evaluated reliably" in w for w in result.warnings))

    def test_unrelated_answer_scores_low_with_no_concepts(self):
        answer = ("I like to cook pasta on weekends with fresh tomatoes and basil from my garden, and then "
                  "I invite my friends over so that we can eat dinner together and watch a movie.")
        result = evaluator.evaluate_answer(answer, SAMPLE_QUESTION)
        self.assertEqual(result.matched_concepts, [])
        self.assertLess(result.total_score, 30)

    def test_good_answer_beats_unrelated_answer(self):
        good = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION).total_score
        bad = evaluator.evaluate_answer("I enjoy hiking in the mountains during summer holidays with my family "
                                        "and friends every single year.", SAMPLE_QUESTION).total_score
        self.assertGreater(good, bad + 30)

    def test_length_alone_does_not_earn_a_high_score(self):
        padded = "the list is a thing that is used in many places and it is good " * 40
        result = evaluator.evaluate_answer(padded, SAMPLE_QUESTION)
        self.assertLess(result.total_score, 35)

    def test_keyword_stuffing_scores_below_a_real_explanation(self):
        stuffed = "mutable immutable cannot be changed faster memory sorted " * 4
        stuffed_result = evaluator.evaluate_answer(stuffed, SAMPLE_QUESTION)
        real_result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        self.assertTrue(any("keywords" in w for w in stuffed_result.warnings))
        self.assertLess(stuffed_result.total_score, real_result.total_score + 20)
        self.assertLess(stuffed_result.breakdown["explanation_quality"]["earned"],
                        real_result.breakdown["explanation_quality"]["earned"] + 5)

    def test_report_depends_on_the_submitted_answer(self):
        a = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        b = evaluator.evaluate_answer(
            "A tuple is faster and uses less memory than a list, and sorted data can be handled by both.",
            SAMPLE_QUESTION)
        self.assertNotEqual(a.matched_concepts, b.matched_concepts)
        self.assertNotEqual(a.strengths, b.strengths)
        # Every concept reported as matched really has a keyword present in the answer.
        normalized = evaluator.normalize_text(GOOD_ANSWER)
        for name, keywords in a.matched_keywords.items():
            self.assertTrue(any(evaluator.contains_phrase(normalized, kw) for kw in keywords), name)

    def test_example_detection(self):
        with_example = GOOD_ANSWER
        without_example = GOOD_ANSWER.replace("For example, ", "")
        self.assertIn("You supported your explanation with an example.",
                      evaluator.evaluate_answer(with_example, SAMPLE_QUESTION).strengths)
        self.assertIn("No example detected.",
                      evaluator.evaluate_answer(without_example, SAMPLE_QUESTION).improvements)


class TestScoring(unittest.TestCase):
    def test_breakdown_adds_up_to_total(self):
        result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        parts = sum(item["earned"] for item in result.breakdown.values())
        self.assertAlmostEqual(parts, result.total_score, delta=0.3)  # rounding only

    def test_default_weights_sum_to_100(self):
        self.assertEqual(sum(evaluator.DEFAULT_WEIGHTS.values()), 100)

    def test_component_maximums_are_never_exceeded(self):
        result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        for item in result.breakdown.values():
            self.assertLessEqual(item["earned"], item["max"])
            self.assertGreaterEqual(item["earned"], 0)

    def test_concept_coverage_math(self):
        # 2 of 3 concepts -> 50 * 2/3 = 33.3
        result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        self.assertAlmostEqual(result.breakdown["concept_coverage"]["earned"], 33.3, places=1)

    def test_scores_stay_between_0_and_100_for_random_text(self):
        rng = random.Random(42)
        words = ["list", "tuple", "mutable", "sorted", "faster", "memory", "banana", "river", "the", "is"]
        for _ in range(200):
            text = " ".join(rng.choice(words + [rng.choice(string.ascii_lowercase)]) for _ in range(rng.randint(1, 120)))
            score = evaluator.evaluate_answer(text, SAMPLE_QUESTION).total_score
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_performance_label_boundaries(self):
        self.assertEqual(evaluator.performance_label(100), "Excellent")
        self.assertEqual(evaluator.performance_label(85), "Excellent")
        self.assertEqual(evaluator.performance_label(84.9), "Good")
        self.assertEqual(evaluator.performance_label(70), "Good")
        self.assertEqual(evaluator.performance_label(69.9), "Fair")
        self.assertEqual(evaluator.performance_label(50), "Fair")
        self.assertEqual(evaluator.performance_label(49.9), "Needs Work")
        self.assertEqual(evaluator.performance_label(30), "Needs Work")
        self.assertEqual(evaluator.performance_label(29.9), "Getting Started")
        self.assertEqual(evaluator.performance_label(0), "Getting Started")

    def test_custom_weights_change_the_score(self):
        heavy_coverage = {"concept_coverage": 80, "relevance": 10, "explanation_quality": 5, "completeness": 5}
        default = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        custom = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION, weights=heavy_coverage)
        self.assertNotEqual(default.total_score, custom.total_score)
        self.assertAlmostEqual(custom.breakdown["concept_coverage"]["earned"], 80 * 2 / 3, places=1)

    def test_invalid_weights_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION, weights={"concept_coverage": 100})
        with self.assertRaises(ValueError):
            evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION, weights={
                "concept_coverage": 60, "relevance": 25, "explanation_quality": 15, "completeness": 10})
        with self.assertRaises(ValueError):
            evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION, weights={
                "concept_coverage": 110, "relevance": -10, "explanation_quality": 0, "completeness": 0})

    def test_result_survives_dict_round_trip(self):
        result = evaluator.evaluate_answer(GOOD_ANSWER, SAMPLE_QUESTION)
        again = evaluator.EvaluationResult.from_dict(result.to_dict())
        self.assertEqual(result, again)


class TestRealQuestionBank(unittest.TestCase):
    def test_every_model_answer_scores_well_and_covers_all_concepts(self):
        for q in question_bank.get_all_questions():
            result = evaluator.evaluate_answer(q["model_answer"], q)
            self.assertEqual(result.missing_concepts, [], f"{q['id']} misses {result.missing_concepts}")
            self.assertGreaterEqual(result.total_score, 80, f"{q['id']} scored {result.total_score}")
            self.assertLessEqual(result.total_score, 100)

    def test_a_model_answer_for_one_question_does_not_pass_another(self):
        questions = question_bank.get_all_questions()
        for i, q in enumerate(questions):
            other = questions[(i + 7) % len(questions)]
            if other["topic"] == q["topic"]:
                other = questions[(i + 13) % len(questions)]
            result = evaluator.evaluate_answer(q["model_answer"], other)
            self.assertLess(result.total_score, 60, f"{q['id']} answer scored on {other['id']}: {result.total_score}")


if __name__ == "__main__":
    unittest.main()
