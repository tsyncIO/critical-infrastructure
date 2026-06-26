from collections import defaultdict
from app.models import Incident, AlarmEvent, TepRun, InfrastructureComponent, IncidentAlarmEvent
from app.extensions import db


def group_incidents(window_size=10):
    alarms = AlarmEvent.query.filter(AlarmEvent.is_duplicate == False).order_by(AlarmEvent.run_id, AlarmEvent.time_step).all()
    incidents = []
    grouped = defaultdict(list)
    for alarm in alarms:
        bucket = (alarm.run_id, alarm.time_step // window_size, alarm.component_key)
        grouped[bucket].append(alarm)
    for (run_id, window, component_key), alarm_list in grouped.items():
        raw_count = len(alarm_list)
        unique_count = len({(a.variable_id, a.alarm_type, a.severity) for a in alarm_list})
        first_ts = min(a.time_step for a in alarm_list)
        last_ts = max(a.time_step for a in alarm_list)
        severity = 'critical' if any(a.severity == 'critical' for a in alarm_list) else 'warning'
        title = component_title(component_key)
        explanation = (
            f"This incident groups {raw_count} raw alarms into {unique_count} unique alarm types "
            f"between time steps {first_ts} and {last_ts}. The dominant affected component is {component_key}. "
            f"Severity is {severity} because {'critical alarms exist' if severity == 'critical' else 'only warning alarms exist'}."
        )
        incident = Incident(
            run_id=run_id,
            title=title,
            root_cause_candidate=component_key,
            severity=severity,
            first_time_step=first_ts,
            last_time_step=last_ts,
            raw_alarm_count=raw_count,
            unique_alarm_count=unique_count,
            affected_component_count=1,
            explanation=explanation,
        )
        db.session.add(incident)
        db.session.flush()
        for alarm in alarm_list:
            db.session.add(IncidentAlarmEvent(incident_id=incident.id, alarm_event_id=alarm.id))
        incidents.append(incident)
    db.session.commit()
    return len(incidents)


def component_title(key: str) -> str:
    mapping = {
        'cooling_system': 'Cooling-system degradation',
        'process_control_system': 'Process-control anomaly',
        'industrial_process': 'Industrial-process instability',
        'port_operations': 'Port-service availability risk',
        'communication_system': 'Communication-system degradation',
    }
    return mapping.get(key, f'{key.replace("_", " ").capitalize()} incident')
