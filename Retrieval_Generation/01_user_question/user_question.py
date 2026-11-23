SAMPLE_QUESTIONS = [
    "What is counterpressing?",
    "What are the weaknesses of a low block?",
    "How does a team build up from the back?",
    "What should players do right after losing the ball?",
    "Who won the 2022 World Cup?",  # hujjatlarda yo'q — tizim javobni o'ylab topmasligi kerak
]


def prepare_question(question: str) -> str:
    """Boshi/oxiridagi bo'sh joylarni olib tashlaydi. Bo'sh savol — xato."""
    question = question.strip()
    if not question:
        raise ValueError("Savol bo'sh bo'lmasligi kerak")
    return question


if __name__ == "__main__":
    for number, question in enumerate(SAMPLE_QUESTIONS, start=1):
        print(f"{number}. {question}")
