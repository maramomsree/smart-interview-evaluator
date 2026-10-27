"""
evaluator.py
============
A transparent, rule-based answer evaluator. It knows NOTHING about Streamlit
or the database, so it can be tested on its own.

SCORING (out of 100, weights are configurable via DEFAULT_WEIGHTS)
------------------------------------------------------------------
A. Concept Coverage (50)   = 50 * (concepts found / concepts expected)
B. Relevance (25)          = how much of the answer's vocabulary belongs to the
                             question's subject (not the question's own words)
C. Explanation Quality (15)= detail (5) + sentence structure (5) + example (5)
D. Completeness (10)       = 10 * (coverage ratio squared): finishing the job
                             is rewarded more than partial coverage

ANTI-GAMING RULES
-----------------
* Length is capped: more than LENGTH_TARGET_WORDS words earns nothing extra.
* Repeated words / keyword lists are detected and penalised.
* Answers shorter than MIN_RELIABLE_WORDS are flagged and capped.

LIMITATIONS (be honest about these in interviews!)
--------------------------------------------------
This is keyword matching, not understanding. It cannot tell that a sentence is
factually wrong ("lists are immutable" still matches the concept "mutability"),
it ignores negation, and correct answers phrased with unexpected words can be
under-scored. The score is an estimate to guide practice, not a verdict on
anyone's ability or interview success.
"""

import re
from dataclasses import asdict, dataclass, field
from functools import lru_cache

# ---------------------------------------------------------------------------
# Configuration (all the "magic numbers" live here so they are easy to tune)
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {
    "concept_coverage": 50,
    "relevance": 25,
    "explanation_quality": 15,
    "completeness": 10,
}
COMPONENT_LABELS = {
    "concept_coverage": "Concept Coverage",
    "relevance": "Relevance",
    "explanation_quality": "Explanation Quality",
    "completeness": "Completeness",
}

MIN_RELIABLE_WORDS = 15        # below this the score is flagged as unreliable
SHORT_ANSWER_SCORE_CAP = 35.0  # ...and capped at this value
LENGTH_TARGET_WORDS = 60       # more words than this earns no extra credit
RELEVANCE_FULL_RATIO = 0.20    # share of on-topic words needed for full relevance marks
KEYWORD_DUMP_DENSITY = 0.60    # if >60% of all words are domain terms it looks like a keyword list
MIN_LEXICAL_DIVERSITY = 0.50   # unique words / total words; lower means heavy repetition
MAX_ANSWER_CHARS = 5000

PERFORMANCE_LABELS = [  # (minimum score, label), checked from the top
    (85, "Excellent"),
    (70, "Good"),
    (50, "Fair"),
    (30, "Needs Work"),
    (0, "Getting Started"),
]

STOPWORDS = frozenset(
    """
    a an the and or but if then else of in on at to for from by with without into onto over under
    is are was were be been being am do does did done has have had having it its this that these
    those there here as so such than too very can could should would will shall may might must
    not no nor yes you your yours we our ours they them their i me my he she his her him about
    also just only more most some any each every other another which who whom what when where why
    how all both either neither up down out off again once same own
    """.split()
)

EXAMPLE_CUES = (
    "for example", "for instance", "e g", "eg", "such as", "suppose", "imagine",
    "in practice", "use case", "say you", "consider",
)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def normalize_text(text):
    """
    Lowercase, drop punctuation and collapse whitespace.

    Characters '+' and '#' are kept because they are meaningful in tech terms
    (c++, c#, v+e). Hyphens and slashes become spaces, so "first-in-first-out"
    and "first in first out" normalize identically.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)
    text = re.sub(r"(?<=[a-z0-9])\s*\+\s*(?=[a-z0-9])", "+", text)  # "v + e" -> "v+e", but "c++ and" is untouched
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=None)
def _phrase_pattern(normalized_phrase):
    """
    Compile a regex that matches a phrase only as WHOLE words.
    (?<![a-z0-9]) / (?![a-z0-9]) are "boundary" checks: they stop 'sorted'
    from matching inside 'unsorted' and 'list' from matching inside 'playlist'.
    The optional suffix lets 'list' also match 'lists' and 'hash' match 'hashed'.
    """
    return re.compile(
        r"(?<![a-z0-9])" + re.escape(normalized_phrase) + r"(?:s|es|d|ed|ing)?(?![a-z0-9])"
    )


def contains_phrase(normalized_text, phrase):
    """True if the (already normalized) text contains the phrase as whole words."""
    normalized_phrase = normalize_text(phrase)
    if not normalized_phrase:
        return False
    return _phrase_pattern(normalized_phrase).search(normalized_text) is not None


def content_words(normalized_text):
    """Meaningful words only: no stopwords, nothing shorter than 3 characters."""
    return [w for w in normalized_text.split() if len(w) >= 3 and w not in STOPWORDS]


def count_sentences(raw_text):
    """Count sentence-like chunks of at least 3 words."""
    chunks = re.split(r"[.!?;\n]+", raw_text)
    return sum(1 for chunk in chunks if len(chunk.split()) >= 3)


# ---------------------------------------------------------------------------
# Result object
# ---------------------------------------------------------------------------
@dataclass
class EvaluationResult:
    total_score: float
    label: str
    breakdown: dict
    matched_concepts: list
    missing_concepts: list          # each item: {"name": ..., "hint": ...}
    total_concepts: int
    matched_keywords: dict          # concept name -> keywords detected
    strengths: list = field(default_factory=list)
    improvements: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    word_count: int = 0
    reliable: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------
def validate_answer(answer):
    """Return (is_ok, message). Used by the UI before calling evaluate_answer."""
    if answer is None or not str(answer).strip():
        return False, "Please write an answer before submitting."
    if len(answer) > MAX_ANSWER_CHARS:
        return False, f"Your answer is too long ({len(answer)} characters). Please keep it under {MAX_ANSWER_CHARS}."
    return True, ""


def performance_label(score):
    """Convert a numeric score into a simple label."""
    for minimum, label in PERFORMANCE_LABELS:
        if score >= minimum:
            return label
    return PERFORMANCE_LABELS[-1][1]


def validate_weights(weights):
    """Return a checked copy of the weights; raise ValueError if they are invalid."""
    if weights is None:
        return dict(DEFAULT_WEIGHTS)
    if set(weights) != set(DEFAULT_WEIGHTS):
        raise ValueError(f"Weights must have exactly these keys: {sorted(DEFAULT_WEIGHTS)}")
    if any(value < 0 for value in weights.values()):
        raise ValueError("Weights cannot be negative.")
    if abs(sum(weights.values()) - 100) > 1e-6:
        raise ValueError(f"Weights must add up to 100 (got {sum(weights.values())}).")
    return dict(weights)


def find_matched_concepts(normalized_answer, concepts):
    """Return {concept name: [keywords found]} for every concept that is present."""
    matched = {}
    for concept in concepts:
        found = [kw for kw in concept["keywords"] if contains_phrase(normalized_answer, kw)]
        if found:
            matched[concept["name"]] = found
    return matched


def domain_vocabulary(question):
    """
    Words that belong to the question's subject: every word inside any concept
    keyword. We intentionally exclude the question's own wording, otherwise an
    answer could earn relevance by merely repeating the question.
    """
    vocab = set()
    for concept in question["concepts"]:
        for keyword in concept["keywords"]:
            vocab.update(content_words(normalize_text(keyword)))
    return vocab


def evaluate_answer(answer, question, weights=None):
    """
    Evaluate `answer` against `question` (a dictionary from question_bank).
    Returns an EvaluationResult. Raises ValueError for empty answers or bad weights.
    """
    weights = validate_weights(weights)
    ok, message = validate_answer(answer)
    if not ok:
        raise ValueError(message)

    concepts = question["concepts"]
    normalized = normalize_text(answer)
    tokens = normalized.split()
    word_count = len(tokens)
    total_concepts = len(concepts)

    # --- Concepts ----------------------------------------------------------
    matched_keywords = find_matched_concepts(normalized, concepts)
    matched_names = [c["name"] for c in concepts if c["name"] in matched_keywords]
    missing = [{"name": c["name"], "hint": c["hint"]} for c in concepts if c["name"] not in matched_keywords]
    coverage_ratio = len(matched_names) / total_concepts if total_concepts else 0.0

    # --- Anti-gaming signals ----------------------------------------------
    vocab = domain_vocabulary(question)
    unique_content = set(content_words(normalized))
    on_topic_ratio = len(unique_content & vocab) / len(unique_content) if unique_content else 0.0
    diversity = len(set(tokens)) / word_count if word_count else 0.0
    density = sum(1 for t in tokens if t in vocab) / word_count if word_count else 0.0
    keyword_dump = word_count >= MIN_RELIABLE_WORDS and (
        density > KEYWORD_DUMP_DENSITY or diversity < MIN_LEXICAL_DIVERSITY
    )

    # --- A. Concept coverage ----------------------------------------------
    coverage_points = weights["concept_coverage"] * coverage_ratio
    coverage_detail = f"{len(matched_names)} of {total_concepts} expected concepts found."

    # --- B. Relevance -----------------------------------------------------
    relevance_fraction = min(1.0, on_topic_ratio / RELEVANCE_FULL_RATIO)
    if not matched_names:
        relevance_fraction *= 0.4  # no expected concept at all: strongly limit relevance
    if keyword_dump:
        relevance_fraction *= 0.5
    relevance_points = weights["relevance"] * relevance_fraction
    relevance_detail = f"{on_topic_ratio:.0%} of your meaningful words are on-topic (full marks at {RELEVANCE_FULL_RATIO:.0%})."

    # --- C. Explanation quality (three equal parts) ------------------------
    sentences = count_sentences(answer)
    has_example = "`" in answer or any(contains_phrase(normalized, cue) for cue in EXAMPLE_CUES)
    third = weights["explanation_quality"] / 3
    detail_part = third * min(1.0, word_count / LENGTH_TARGET_WORDS)
    structure_part = third * min(1.0, sentences / 3)
    example_part = third if has_example else 0.0
    quality_points = detail_part + structure_part + example_part
    if keyword_dump:
        quality_points *= 0.3
    quality_detail = (
        f"{word_count} words (credit stops at {LENGTH_TARGET_WORDS}), "
        f"{sentences} sentence(s), example {'found' if has_example else 'not found'}."
    )

    # --- D. Completeness --------------------------------------------------
    completeness_points = weights["completeness"] * (coverage_ratio ** 2)
    completeness_detail = f"Coverage ratio {coverage_ratio:.2f} squared, so covering everything matters most."

    raw_total = coverage_points + relevance_points + quality_points + completeness_points

    # --- Warnings and caps -------------------------------------------------
    warnings = []
    reliable = word_count >= MIN_RELIABLE_WORDS
    if not reliable:
        raw_total = min(raw_total, SHORT_ANSWER_SCORE_CAP)
        warnings.append(
            f"Your answer has only {word_count} word(s). Answers under {MIN_RELIABLE_WORDS} words cannot be "
            f"evaluated reliably, so the score is capped at {SHORT_ANSWER_SCORE_CAP:g}."
        )
    if keyword_dump:
        warnings.append(
            "Your answer looks like a list of keywords or repeats the same words. Write full sentences that "
            "explain each idea; keyword lists receive reduced credit."
        )
    total = round(max(0.0, min(100.0, raw_total)), 1)

    breakdown = {
        "concept_coverage": {"earned": round(coverage_points, 1), "max": weights["concept_coverage"], "detail": coverage_detail},
        "relevance": {"earned": round(relevance_points, 1), "max": weights["relevance"], "detail": relevance_detail},
        "explanation_quality": {"earned": round(quality_points, 1), "max": weights["explanation_quality"], "detail": quality_detail},
        "completeness": {"earned": round(completeness_points, 1), "max": weights["completeness"], "detail": completeness_detail},
    }
    for key, entry in breakdown.items():
        entry["label"] = COMPONENT_LABELS[key]

    # --- Feedback built from THIS answer ----------------------------------
    strengths, improvements, suggestions = [], [], []
    for name in matched_names:
        shown = ", ".join(f"'{kw}'" for kw in matched_keywords[name][:3])
        strengths.append(f"Covered '{name}' (detected: {shown}).")
    if has_example:
        strengths.append("You supported your explanation with an example.")
    if reliable and word_count >= LENGTH_TARGET_WORDS and sentences >= 3 and not keyword_dump:
        strengths.append("Your answer is developed in several full sentences.")

    for item in missing:
        improvements.append(f"Missing concept: '{item['name']}'.")
        suggestions.append(item["hint"])
    if not has_example:
        improvements.append("No example detected.")
        suggestions.append("Add a short, concrete example (start with 'For example...').")
    if reliable and word_count < LENGTH_TARGET_WORDS * 0.5:
        improvements.append("The explanation is brief.")
        suggestions.append("Explain the 'why' behind each point, not just the terms.")
    if matched_names and on_topic_ratio < RELEVANCE_FULL_RATIO * 0.5:
        improvements.append("A large part of the answer does not relate to the topic.")
        suggestions.append("Stay focused on the question; remove side topics.")
    if not matched_names:
        suggestions.append("Start with a one-sentence definition that uses the key terms for this topic.")
    if not missing:
        suggestions.append("All expected concepts were detected. Practice delivering this in 60-90 seconds out loud.")

    return EvaluationResult(
        total_score=total,
        label=performance_label(total),
        breakdown=breakdown,
        matched_concepts=matched_names,
        missing_concepts=missing,
        total_concepts=total_concepts,
        matched_keywords=matched_keywords,
        strengths=strengths,
        improvements=improvements,
        suggestions=suggestions,
        warnings=warnings,
        word_count=word_count,
        reliable=reliable,
    )
