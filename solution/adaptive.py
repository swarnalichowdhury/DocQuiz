"""The adaptive engine — the part that makes DocQuiz feel like a tutor.

Pure logic, no database, no web, no AI calls. It gets two plain inputs and
returns one question. That separation is deliberate: you can reason about
(and test) this file on its own.
"""

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


def pick_next_question(unanswered: list[dict], topic_stats: dict[str, dict]) -> dict | None:
    """Pick the next question to ask, favouring weak topics.

    unanswered:  questions not yet answered (each has topic + difficulty).
    topic_stats: {topic: {"correct": n, "total": n}} from answered so far.

    Strategy:
    1. No questions left -> None (quiz over).
    2. Find the topic you're weakest in (lowest accuracy). A topic you
       haven't been asked about yet counts as 0.5 — neither strong nor weak.
    3. Within that topic, pick difficulty based on your accuracy there:
       below 50% -> easy, below 80% -> medium, otherwise -> hard.
    4. If no question of that exact difficulty is left in the topic, fall
       back through easy -> medium -> hard.
    """
    if not unanswered:
        return None

    def accuracy(topic: str) -> float:
        stats = topic_stats.get(topic)
        if not stats or stats["total"] == 0:
            return 0.5
        return stats["correct"] / stats["total"]

    weakest = min(unanswered, key=lambda q: accuracy(q["topic"]))
    target_topic = weakest["topic"]
    candidates = [q for q in unanswered if q["topic"] == target_topic]

    acc = accuracy(target_topic)
    if acc < 0.5:
        desired = "easy"
    elif acc < 0.8:
        desired = "medium"
    else:
        desired = "hard"

    for difficulty in [desired] + DIFFICULTY_ORDER:
        for q in candidates:
            if q["difficulty"] == difficulty:
                return q
    return candidates[0]
