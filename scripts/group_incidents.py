from app import create_app
from app.services.incident_grouper import group_incidents


def main():
    app = create_app()
    with app.app_context():
        count = group_incidents(window_size=10)
        print(f'Created {count} incidents from filtered alarms.')


if __name__ == '__main__':
    main()
