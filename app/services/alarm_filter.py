from app.models import AlarmEvent, TepRun
from app.extensions import db


def mark_duplicate_alarms(window=3):
    alarms = AlarmEvent.query.order_by(AlarmEvent.run_id, AlarmEvent.variable_id, AlarmEvent.time_step).all()
    last_seen = {}
    for alarm in alarms:
        key = (alarm.run_id, alarm.variable_id, alarm.alarm_type, alarm.severity)
        if key in last_seen and alarm.time_step - last_seen[key] <= window:
            alarm.is_duplicate = True
            alarm.duplicate_group_key = f'{key[0]}-{key[1]}-{key[2]}-{key[3]}-{alarm.time_step}'
        else:
            alarm.is_duplicate = False
            alarm.duplicate_group_key = None
        last_seen[key] = alarm.time_step
    db.session.commit()
    return len(alarms)
