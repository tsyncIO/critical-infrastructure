from app import create_app
from app.services.alarm_generator import generate_alarms_for_run


def main():
    app = create_app()
    with app.app_context():
        created = generate_alarms_for_run(dataset_role='faulty_testing')
        print(f'Generated {created} alarm events for faulty testing runs.')


if __name__ == '__main__':
    main()
