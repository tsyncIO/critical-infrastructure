"""test_incident_grouping.py – Tests for incident creation from grouped alarms."""
import pytest
from app.models import (
    RawDatasetFile, TepRun, SensorVariable, AlarmEvent, Incident
)
from app.services.incident_grouper import group_incidents, component_title


def _seed_alarm(db, run_id, var_id, time_step, severity='warning', component_key='cooling_system'):
    a = AlarmEvent(
        run_id=run_id,
        time_step=time_step,
        variable_id=var_id,
        component_key=component_key,
        alarm_type='warning_high_alarm',
        severity=severity,
        message='test',
        is_duplicate=False,
    )
    db.session.add(a)
    return a


def test_related_alarms_create_one_incident(app, db):
    """Alarms in the same time window and component must produce exactly one incident."""
    with app.app_context():
        file = RawDatasetFile(file_name='grp_test.RData', file_path='Data/grp_test.RData', dataset_role='faulty_testing')
        db.session.add(file)
        db.session.flush()
        run = TepRun(dataset_file_id=file.id, run_id='grp-1-1', dataset_role='faulty_testing',
                     fault_id=1, fault_label='fault_1', is_faulty=True)
        db.session.add(run)
        db.session.flush()
        var = SensorVariable(variable_name='xmeas_grp', component_key='cooling_system')
        db.session.add(var)
        db.session.flush()

        # Three alarms in the same 10-step window (t=10..19) for cooling_system
        for t in [10, 12, 15]:
            _seed_alarm(db, run.id, var.id, t, component_key='cooling_system')
        db.session.commit()

        count = group_incidents(window_size=10)
        assert count >= 1

        incident = Incident.query.filter_by(run_id=run.id).first()
        assert incident is not None
        assert incident.raw_alarm_count == 3


def test_incident_severity_critical_if_any_critical_alarm(app, db):
    """Incident severity must be critical when at least one unique alarm is critical."""
    with app.app_context():
        file = RawDatasetFile(file_name='sev_test.RData', file_path='Data/sev_test.RData', dataset_role='faulty_testing')
        db.session.add(file)
        db.session.flush()
        run = TepRun(dataset_file_id=file.id, run_id='sev-1-1', dataset_role='faulty_testing',
                     fault_id=1, fault_label='fault_1', is_faulty=True)
        db.session.add(run)
        db.session.flush()
        var = SensorVariable(variable_name='xmeas_sev', component_key='industrial_process')
        db.session.add(var)
        db.session.flush()

        _seed_alarm(db, run.id, var.id, 5, severity='warning', component_key='industrial_process')
        crit = AlarmEvent(
            run_id=run.id, time_step=7, variable_id=var.id,
            component_key='industrial_process', alarm_type='critical_high_alarm',
            severity='critical', message='critical test', is_duplicate=False,
        )
        db.session.add(crit)
        db.session.commit()

        group_incidents(window_size=10)

        incident = Incident.query.filter_by(run_id=run.id).first()
        assert incident is not None
        assert incident.severity == 'critical'


def test_component_title_mapping():
    """component_title must return meaningful human-readable titles."""
    assert 'cooling' in component_title('cooling_system').lower()
    assert 'control' in component_title('process_control_system').lower()
    assert 'port' in component_title('port_operations').lower()
