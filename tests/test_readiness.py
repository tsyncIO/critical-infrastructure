"""test_readiness.py – Tests for readiness scoring logic."""
import pytest
from app.models import ReadinessQuestion, ReadinessAssessment, ReadinessAnswer
from app.services.readiness_score import score_assessment, SCORE_MAP


def _seed_questions(db):
    questions = [
        ReadinessQuestion(question_key='q_yes_test', question_text='Test yes?', category='Test', weight=1.0),
        ReadinessQuestion(question_key='q_partial_test', question_text='Test partial?', category='Test', weight=2.0),
        ReadinessQuestion(question_key='q_no_test', question_text='Test no?', category='Test', weight=1.5),
    ]
    db.session.add_all(questions)
    db.session.commit()


def test_score_map_values():
    """Score map must assign correct numeric values."""
    assert SCORE_MAP['yes'] == 1.0
    assert SCORE_MAP['partial'] == 0.5
    assert SCORE_MAP['no'] == 0.0
    assert SCORE_MAP['unknown'] == 0.0


def test_yes_partial_no_produces_correct_weighted_score(app, db):
    """yes(w=1)+partial(w=2)+no(w=1.5) → weighted=(1*1 + 0.5*2 + 0*1.5)=2.0, max=4.5."""
    with app.app_context():
        _seed_questions(db)
        responses = [
            {'question_key': 'q_yes_test', 'answer_value': 'yes'},
            {'question_key': 'q_partial_test', 'answer_value': 'partial'},
            {'question_key': 'q_no_test', 'answer_value': 'no'},
        ]
        assessment = score_assessment(responses, title='Unit Test Assessment')
        assert assessment.total_score == pytest.approx(2.0, abs=0.01)
        assert assessment.max_score == pytest.approx(4.5, abs=0.01)
        expected_pct = 2.0 / 4.5 * 100
        assert assessment.percentage_score == pytest.approx(expected_pct, abs=0.1)


def test_all_yes_produces_100_percent(app, db):
    """All 'yes' answers should produce 100% score."""
    with app.app_context():
        responses = [
            {'question_key': 'q_yes_test', 'answer_value': 'yes'},
            {'question_key': 'q_partial_test', 'answer_value': 'yes'},
            {'question_key': 'q_no_test', 'answer_value': 'yes'},
        ]
        assessment = score_assessment(responses, title='All Yes Test')
        assert assessment.percentage_score == pytest.approx(100.0, abs=0.1)


def test_all_no_produces_zero_percent(app, db):
    """All 'no' answers should produce 0% score."""
    with app.app_context():
        responses = [
            {'question_key': 'q_yes_test', 'answer_value': 'no'},
            {'question_key': 'q_partial_test', 'answer_value': 'no'},
            {'question_key': 'q_no_test', 'answer_value': 'no'},
        ]
        assessment = score_assessment(responses, title='All No Test')
        assert assessment.percentage_score == pytest.approx(0.0, abs=0.1)


def test_unknown_answer_same_as_no(app, db):
    """'unknown' answer must score the same as 'no' (0.0)."""
    with app.app_context():
        r1 = [{'question_key': 'q_yes_test', 'answer_value': 'no'}]
        r2 = [{'question_key': 'q_yes_test', 'answer_value': 'unknown'}]
        a1 = score_assessment(r1, title='No Test')
        a2 = score_assessment(r2, title='Unknown Test')
        assert a1.total_score == a2.total_score


def test_assessment_saved_to_database(app, db):
    """score_assessment must persist the assessment record."""
    with app.app_context():
        initial_count = ReadinessAssessment.query.count()
        score_assessment(
            [{'question_key': 'q_yes_test', 'answer_value': 'yes'}],
            title='Persistence test'
        )
        assert ReadinessAssessment.query.count() == initial_count + 1
