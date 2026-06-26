import json
from app import create_app
from app.services.readiness_score import score_assessment


def main():
    app = create_app()
    with app.app_context():
        answers_file = 'data/readiness_answers.json'
        try:
            with open(answers_file, 'r', encoding='utf-8') as handle:
                payload = json.load(handle)
        except FileNotFoundError:
            payload = [
                {'question_key': 'dependencies_documented', 'answer_value': 'yes'},
                {'question_key': 'backup_power_available', 'answer_value': 'partial'},
                {'question_key': 'alternative_communication_available', 'answer_value': 'yes'},
            ]
        assessment = score_assessment(payload)
        print(f'Created readiness assessment {assessment.id} with {assessment.percentage_score:.1f}% score.')


if __name__ == '__main__':
    main()
