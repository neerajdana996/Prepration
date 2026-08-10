"""M5.13 - Reflexion: an agent that learns from its OWN failures across attempts.

Loop: attempt -> check -> if it fails, REFLECT into a one-line 'lesson' -> store it
-> retry with the lessons in context. Watch it fail, learn, then pass.

Three levels of 'self-fixing':
  1. in-run self-correction  (errors-as-observations, m5_03)
  2. cross-attempt reflexion  (THIS file: a lesson memory that persists across tries)
  3. system-level            (feed production failures into the eval set -> fix prompt/model)

Cost note: each retry + reflection is extra LLM calls, so use Reflexion where
correctness matters and latency allows — NOT on a 50k-req/s hot path.

Needs GOOGLE_API_KEY. Run:  cd Topics/SAP-FDE/lab && uv run python agents/m5_13_reflexion.py
"""
from _llm import get_llm

TASK = (
    "Summarize this support ticket in UNDER 8 words, and you MUST include the word 'refund'.\n"
    "Ticket: 'Customer was double-charged on an invoice and is asking for their money back.'"
)


def _text(c) -> str:
    return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c if isinstance(b, dict))


def check(answer: str):
    """A verifiable success criterion (so 'failure' is objective)."""
    if "refund" not in answer.lower():
        return False, "missing the required word 'refund'"
    n = len(answer.split())
    if n >= 8:
        return False, f"too long ({n} words; must be under 8)"
    return True, "ok"


def run(max_attempts: int = 4):
    llm = get_llm(temperature=0.4)
    lessons: list[str] = []  # the agent's growing memory of what NOT to do

    for attempt in range(1, max_attempts + 1):
        prompt = TASK
        if lessons:
            prompt += "\n\nLessons from your past attempts (follow them):\n- " + "\n- ".join(lessons)
        answer = _text(llm.invoke(prompt).content).strip()

        ok, reason = check(answer)
        print(f"attempt {attempt}: {answer!r}  ->  {'PASS' if ok else 'FAIL: ' + reason}")
        if ok:
            print(f"\nSolved in {attempt} attempt(s). Lessons it learned: {lessons}")
            return answer

        # REFLECT: turn this failure into a durable one-line lesson
        lesson = _text(get_llm(temperature=0).invoke(
            f"Your answer '{answer}' failed because: {reason}. "
            "Write ONE short imperative lesson (max 12 words) to avoid this next time."
        ).content).strip()
        lessons.append(lesson)
        print(f"           reflected -> lesson: {lesson!r}")

    print("\nHit max attempts without passing.")
    return None


def main() -> None:
    run()


if __name__ == "__main__":
    main()
