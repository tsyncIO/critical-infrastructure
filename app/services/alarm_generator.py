from app.models import AlarmEvent, TepRun, SensorVariable, VariableStatistic, SensorObservation
from app.extensions import db


SEVERITY_MAP = {
    'critical_low_alarm': 'critical',
    'critical_high_alarm': 'critical',
    'warning_low_alarm': 'warning',
    'warning_high_alarm': 'warning',
}


def determine_alarm(value, stats):
    if value < stats.critical_low:
        return 'critical_low_alarm', stats.critical_low
    if value > stats.critical_high:
        return 'critical_high_alarm', stats.critical_high
    if value < stats.warning_low:
        return 'warning_low_alarm', stats.warning_low
    if value > stats.warning_high:
        return 'warning_high_alarm', stats.warning_high
    return None, None


def generate_alarms_for_run(run_id=None, dataset_role=None, limit=0):
    query = SensorObservation.query.join(TepRun, SensorObservation.run_id == TepRun.id)
    if dataset_role:
        query = query.filter(TepRun.dataset_role == dataset_role)
    if run_id:
        query = query.filter(TepRun.run_id == run_id)
    if limit:
        query = query.limit(limit)
    observations = query.all()

    variables = {v.id: v for v in SensorVariable.query.all()}
    stats = {s.variable_id: s for s in VariableStatistic.query.all()}

    events = []
    for obs in observations:
        stat = stats.get(obs.variable_id)
        if not stat:
            continue
        alarm_type, threshold_value = determine_alarm(obs.variable_value, stat)
        if not alarm_type:
            continue
        severity = SEVERITY_MAP[alarm_type]
        message = f"{variables[obs.variable_id].variable_name} is {'below' if 'low' in alarm_type else 'above'} {severity} threshold at time step {obs.time_step}. Value={obs.variable_value}, threshold={threshold_value}."
        event = AlarmEvent(
            run_id=obs.run_id,
            observation_id=obs.id,
            time_step=obs.time_step,
            variable_id=obs.variable_id,
            component_key=variables[obs.variable_id].component_key,
            alarm_type=alarm_type,
            severity=severity,
            message=message,
            deviation_value=abs(obs.variable_value - threshold_value),
            threshold_value=threshold_value,
        )
        events.append(event)
    if events:
        db.session.bulk_save_objects(events)
        db.session.commit()
    return len(events)
