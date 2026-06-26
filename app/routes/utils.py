from app.models import (
    TepRun, AlarmEvent, Incident, ReadinessAssessment,
    SensorObservation, SensorVariable, RawDatasetFile, SimulationRun,
)


def get_overview_summary():
    recent_incidents = (
        Incident.query
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        'total_runs':           TepRun.query.count(),
        'total_observations':   SensorObservation.query.count(),
        'total_alarms':         AlarmEvent.query.count(),
        'critical_alarms':      AlarmEvent.query.filter_by(severity='critical').count(),
        'total_incidents':      Incident.query.count(),
        'total_simulations':    SimulationRun.query.count(),
        'total_files':          RawDatasetFile.query.count(),
        'total_variables':      SensorVariable.query.count(),
        'latest_readiness':     ReadinessAssessment.query.order_by(
                                    ReadinessAssessment.created_at.desc()
                                ).first(),
        'recent_incidents':     recent_incidents,
    }
