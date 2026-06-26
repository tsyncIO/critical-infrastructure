from app import create_app
from app.services.alarm_filter import mark_duplicate_alarms


def main():
    app = create_app()
    with app.app_context():
        count = mark_duplicate_alarms(window=3)
        print(f'Marked duplicate alarms in {count} total alarm events.')


if __name__ == '__main__':
    main()
