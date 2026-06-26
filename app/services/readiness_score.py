from app.models import ReadinessQuestion, ReadinessAssessment, ReadinessAnswer
from app.extensions import db

SCORE_MAP = {
    'yes': 1.0,
    'partial': 0.5,
    'no': 0.0,
    'unknown': 0.0,
}


def score_assessment(responses: list[dict], title: str = 'Readiness Assessment') -> ReadinessAssessment:
    questions = {q.question_key: q for q in ReadinessQuestion.query.all()}
    total = 0.0
    max_score = 0.0
    assessment = ReadinessAssessment(title=title)
    db.session.add(assessment)
    db.session.flush()
    for item in responses:
        question = questions.get(item['question_key'])
        if not question:
            continue
        score = SCORE_MAP.get(item['answer_value'], 0.0)
        weighted = score * question.weight
        total += weighted
        max_score += question.weight
        answer = ReadinessAnswer(
            assessment_id=assessment.id,
            question_id=question.id,
            answer_value=item['answer_value'],
            numeric_score=score,
            comment=item.get('comment'),
        )
        db.session.add(answer)
    assessment.total_score = total
    assessment.max_score = max_score
    assessment.percentage_score = (total / max_score * 100) if max_score else 0.0
    db.session.commit()
    return assessment
