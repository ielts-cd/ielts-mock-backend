# IELTS Band conversion tables
LISTENING_BAND_TABLE = [
    [39, 9], [37, 8.5], [35, 8], [32, 7.5], [30, 7], [26, 6.5], [23, 6],
    [18, 5.5], [16, 5], [13, 4.5], [10, 4], [8, 3.5], [6, 3], [4, 2.5],
]

READING_ACADEMIC_BAND_TABLE = [
    [39, 9], [37, 8.5], [35, 8], [33, 7.5], [30, 7], [27, 6.5], [23, 6],
    [19, 5.5], [15, 5], [13, 4.5], [10, 4], [8, 3.5], [6, 3],
]

READING_GT_BAND_TABLE = [
    [40, 9], [39, 8.5], [37, 8], [36, 7.5], [34, 7], [32, 6.5], [30, 6],
    [27, 5.5], [23, 5], [19, 4.5], [15, 4], [12, 3.5], [9, 3],
]


def pct_to_band(pct):
    if pct is None:
        return None
    raw = (pct / 100) * 9
    return round(max(0, min(9, raw)) * 2) / 2


def raw_to_band(correct, total, table):
    if total is None or total <= 0 or correct is None:
        return None
    scaled = (correct / total) * 40
    for min_raw, band in table:
        if scaled >= min_raw:
            return band
    return 0


def reading_band_table(exam_type):
    return READING_ACADEMIC_BAND_TABLE if exam_type == 'academic' else READING_GT_BAND_TABLE


def criteria_to_band(criteria):
    if not criteria:
        return None
    vals = [v for v in criteria.values() if v is not None]
    if not vals:
        return None
    avg = sum(vals) / len(vals)
    return round(max(0, min(9, avg)) * 2) / 2


def writing_overall_band(task1_band, task2_band):
    if task1_band is None and task2_band is None:
        return None
    t1 = task1_band if task1_band is not None else task2_band
    t2 = task2_band if task2_band is not None else task1_band
    return round(((t1 * 1 + t2 * 2) / 3) * 2) / 2


def is_answer_correct(question, given_answer):
    """Check if an answer is correct based on question type"""
    answer_type = question.get('answerType', 'mcq')

    if answer_type == 'text':
        return is_text_answer_correct(question, given_answer)

    if answer_type == 'multi':
        correct = sorted(question.get('correctIndexes', []))
        given = sorted(given_answer) if isinstance(given_answer, list) else []
        return len(correct) > 0 and correct == given

    # mcq
    return given_answer == question.get('correctIndex')


def is_text_answer_correct(question, given):
    parts = question.get('parts', [])
    blanks = [p for p in parts if p.get('type') == 'blank']

    if not blanks:
        expected = (question.get('correctText') or '').strip().lower()
        actual = (given or '').strip().lower()
        return bool(expected) and actual == expected

    g = given if isinstance(given, dict) else {}
    return all(
        (b.get('correct') or '').strip().lower() == (g.get(b.get('id'), '') or '').strip().lower()
        for b in blanks
    )


def is_question_answered(question, given):
    """Check if a question has been answered (not necessarily correct)"""
    answer_type = question.get('answerType', 'mcq')

    if answer_type == 'text':
        parts = question.get('parts', [])
        blanks = [p for p in parts if p.get('type') == 'blank']
        if not blanks:
            return bool(given and str(given).strip())
        g = given if isinstance(given, dict) else {}
        return any(str(g.get(b.get('id'), '')).strip() for b in blanks)

    if answer_type == 'multi':
        return isinstance(given, list) and len(given) > 0

    return given is not None


def has_answer(question, given):
    """Alias for is_question_answered"""
    return is_question_answered(question, given)