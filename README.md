# 🎯 Smart Interview Answer Evaluator
https://smart-interview-evaluator-dwzev6q8jrmamcxniayh4l.streamlit.app/
A local Streamlit app for practicing technical interview questions. You answer in your own words and get
transparent, concept-based feedback: what you covered, what you missed, how the score was calculated, and a
model answer to learn from. Your progress is stored in a local SQLite database.

## Problem statement

Practicing interview answers alone is hard: you rarely know which important ideas you left out. This project
gives instant, explainable feedback without paid AI services, so you can see exactly *why* an answer scored
the way it did.

## Features

- Dashboard with totals, average score, sessions, recent activity and a progress chart
- Curated library of 36 questions across 6 topics and 3 difficulty levels
- Practice mode with topic / difficulty / keyword filters, draft saving and input validation
- Rule-based evaluator scored out of 100 with a full breakdown
- Detailed feedback report: strengths, missing concepts, suggestions, model answer and answer structure
- SQLite practice history (earlier attempts are never overwritten)
- Analytics with cautious conclusions (topic rankings need enough data)
- CSV export of practice history

## Technologies

Python 3.10+, Streamlit, SQLite (`sqlite3`), pandas (installed with Streamlit, used for tables and charts),
`unittest` for tests. No paid services and no API keys.

## How the evaluation works

Each question stores *expected concepts*, and each concept lists phrases that count as mentioning it.

| Component | Points | How it is calculated |
|---|---|---|
| Concept coverage | 50 | `50 × concepts found / concepts expected` |
| Relevance | 25 | Share of your meaningful words that belong to the question's subject (full marks at 20%) |
| Explanation quality | 15 | Detail (up to 60 words), sentence structure (3+ sentences) and an example, 5 points each |
| Completeness | 10 | `10 × (coverage ratio)²`, so covering everything is rewarded most |

Safeguards: text is lowercased and punctuation removed; phrases match only as whole words (`sorted` does not
match `unsorted`); length beyond 60 words earns nothing extra; keyword lists and heavy repetition are penalised;
answers under 15 words are flagged as unreliable and capped at 35. The weights live in
`evaluator.DEFAULT_WEIGHTS` and can be changed (they must add up to 100).

### Example evaluation

Question: *What is the difference between a list and a tuple in Python?*

Answer: *"A list is mutable so you can change it after creating it, but a tuple is immutable. Tuples are usually
faster and use less memory."*

Actual output of the evaluator for this answer:

```
Score: 68.2 (Fair), 2/3 concepts
  Concept Coverage    33.3 / 50
  Relevance           25.0 / 25
  Explanation Quality  5.4 / 15
  Completeness         4.4 / 10
Strengths: Covered 'Mutability'; Covered 'Performance and memory'
Gaps:      Missing concept 'Use cases'; no example detected; explanation is brief
```

## Project structure

```
smart-interview-evaluator/
├── app.py              # Streamlit UI (display and input only)
├── evaluator.py        # Rule-based scoring engine (no UI, no database)
├── database.py         # SQLite storage (all SQL lives here)
├── question_bank.py    # Question data + search/filter helpers
├── analytics.py        # Statistics and CSV export (pure functions)
├── requirements.txt
├── .streamlit/config.toml   # Theme
├── tests/              # unittest test suite
└── data/               # practice.db is created here (ignored by Git)
```

## Installation

```bash
python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# Windows (cmd):         venv\Scripts\activate.bat
# macOS / Linux:         source venv/bin/activate
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

## Run the tests

```bash
python -m unittest discover -v
```

## Adding questions

Copy an entry in `question_bank.py`, give it a new unique `id`, and edit the text and concepts. The tests
check that the bank is well formed and that every model answer scores well against its own question.

## Known limitations

- Keyword matching does not understand meaning. It cannot detect a wrong statement that uses the right terms
  ("lists are immutable" still matches *Mutability*), and it ignores negation.
- Correct answers phrased with unexpected vocabulary can be under-scored.
- Relevance is a vocabulary-overlap estimate, not true topic understanding.
- The score is an estimate for practice, not a measure of ability or interview success.
- The history is stored per computer in a local file; there are no user accounts.

## Future improvements

Optional semantic evaluation with an AI model (would send your answers to an external service, so it should be
opt-in), follow-up questions, role-specific question sets, a timed interview session mode, and a hosted demo.
