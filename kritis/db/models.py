from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class RawDatasetFile(db.Model):
    __tablename__ = 'raw_dataset_files'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False)
    file_size_bytes = db.Column(db.BigInteger)
    dataset_role = db.Column(db.String(50), nullable=False)
    loaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class TepRun(db.Model):
    __tablename__ = 'tep_runs'

    id = db.Column(db.Integer, primary_key=True)
    dataset_file_id = db.Column(db.Integer, db.ForeignKey('raw_dataset_files.id', ondelete='CASCADE'), nullable=False)
    run_id = db.Column(db.String(100), nullable=False)
    dataset_role = db.Column(db.String(50), nullable=False)
    fault_id = db.Column(db.Integer)
    fault_label = db.Column(db.String(150))
    is_faulty = db.Column(db.Boolean, nullable=False)
    row_count = db.Column(db.Integer)
    variable_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dataset_file = db.relationship('RawDatasetFile', backref=db.backref('tep_runs', lazy=True))


class SensorVariable(db.Model):
    __tablename__ = 'sensor_variables'

    id = db.Column(db.Integer, primary_key=True)
    variable_name = db.Column(db.String(100), nullable=False, unique=True)
    display_name = db.Column(db.String(150))
    variable_group = db.Column(db.String(100))
    component_key = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    description = db.Column(db.Text)


class SensorObservation(db.Model):
    __tablename__ = 'sensor_observations'

    id = db.Column(db.BigInteger, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('tep_runs.id', ondelete='CASCADE'), nullable=False)
    time_step = db.Column(db.Integer, nullable=False)
    variable_id = db.Column(db.Integer, db.ForeignKey('sensor_variables.id', ondelete='CASCADE'), nullable=False)
    variable_value = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tep_run = db.relationship('TepRun', backref=db.backref('sensor_observations', lazy=True))
    variable = db.relationship('SensorVariable', backref=db.backref('sensor_observations', lazy=True))


class VariableStatistic(db.Model):
    __tablename__ = 'variable_statistics'

    id = db.Column(db.Integer, primary_key=True)
    variable_id = db.Column(db.Integer, db.ForeignKey('sensor_variables.id', ondelete='CASCADE'), nullable=False)
    baseline_mean = db.Column(db.Float)
    baseline_std = db.Column(db.Float)
    q001 = db.Column(db.Float)
    q005 = db.Column(db.Float)
    q025 = db.Column(db.Float)
    q500 = db.Column(db.Float)
    q975 = db.Column(db.Float)
    q995 = db.Column(db.Float)
    q999 = db.Column(db.Float)
    warning_low = db.Column(db.Float)
    warning_high = db.Column(db.Float)
    critical_low = db.Column(db.Float)
    critical_high = db.Column(db.Float)
    derived_from_role = db.Column(db.String(50), default='fault_free_training')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variable = db.relationship('SensorVariable', backref=db.backref('statistics', lazy=True))
    __table_args__ = (db.UniqueConstraint('variable_id', 'derived_from_role', name='uq_variable_role'),)


class AlarmEvent(db.Model):
    __tablename__ = 'alarm_events'

    id = db.Column(db.BigInteger, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('tep_runs.id', ondelete='CASCADE'), nullable=False)
    observation_id = db.Column(db.BigInteger, db.ForeignKey('sensor_observations.id', ondelete='SET NULL'))
    time_step = db.Column(db.Integer, nullable=False)
    variable_id = db.Column(db.Integer, db.ForeignKey('sensor_variables.id', ondelete='SET NULL'))
    component_key = db.Column(db.String(100))
    alarm_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, nullable=False)
    deviation_value = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    is_duplicate = db.Column(db.Boolean, default=False)
    duplicate_group_key = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tep_run = db.relationship('TepRun', backref=db.backref('alarm_events', lazy=True))
    observation = db.relationship('SensorObservation', backref=db.backref('alarm_events', lazy=True))
    variable = db.relationship('SensorVariable', backref=db.backref('alarm_events', lazy=True))


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.BigInteger, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('tep_runs.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    root_cause_candidate = db.Column(db.String(150))
    severity = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(50), default='open')
    first_time_step = db.Column(db.Integer)
    last_time_step = db.Column(db.Integer)
    raw_alarm_count = db.Column(db.Integer, default=0)
    unique_alarm_count = db.Column(db.Integer, default=0)
    affected_component_count = db.Column(db.Integer, default=0)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tep_run = db.relationship('TepRun', backref=db.backref('incidents', lazy=True))


class IncidentAlarmEvent(db.Model):
    __tablename__ = 'incident_alarm_events'

    incident_id = db.Column(db.BigInteger, db.ForeignKey('incidents.id', ondelete='CASCADE'), primary_key=True)
    alarm_event_id = db.Column(db.BigInteger, db.ForeignKey('alarm_events.id', ondelete='CASCADE'), primary_key=True)

    incident = db.relationship('Incident', backref=db.backref('incident_alarm_events', lazy=True))
    alarm_event = db.relationship('AlarmEvent', backref=db.backref('incident_alarm_events', lazy=True))


class InfrastructureComponent(db.Model):
    __tablename__ = 'infrastructure_components'

    id = db.Column(db.Integer, primary_key=True)
    component_key = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(150), nullable=False)
    sector = db.Column(db.String(100))
    responsible_org = db.Column(db.String(150))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InfrastructureDependency(db.Model):
    __tablename__ = 'infrastructure_dependencies'

    id = db.Column(db.Integer, primary_key=True)
    source_component_id = db.Column(db.Integer, db.ForeignKey('infrastructure_components.id', ondelete='CASCADE'), nullable=False)
    target_component_id = db.Column(db.Integer, db.ForeignKey('infrastructure_components.id', ondelete='CASCADE'), nullable=False)
    dependency_type = db.Column(db.String(100))
    criticality = db.Column(db.String(30))
    description = db.Column(db.Text)

    source_component = db.relationship('InfrastructureComponent', foreign_keys=[source_component_id], backref=db.backref('outgoing_dependencies', lazy=True))
    target_component = db.relationship('InfrastructureComponent', foreign_keys=[target_component_id], backref=db.backref('incoming_dependencies', lazy=True))

    __table_args__ = (db.UniqueConstraint('source_component_id', 'target_component_id', name='uq_component_dependency'),)


class BcmProfile(db.Model):
    __tablename__ = 'bcm_profiles'

    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('infrastructure_components.id', ondelete='CASCADE'), unique=True, nullable=False)
    maximum_tolerable_downtime_min = db.Column(db.Integer, nullable=False)
    recovery_time_objective_min = db.Column(db.Integer, nullable=False)
    backup_available = db.Column(db.Boolean, default=False)
    backup_duration_min = db.Column(db.Integer)
    recovery_action = db.Column(db.Text)
    emergency_contact_role = db.Column(db.String(150))
    last_exercise_date = db.Column(db.Date)

    component = db.relationship('InfrastructureComponent', backref=db.backref('bcm_profile', uselist=False))


class SimulationRun(db.Model):
    __tablename__ = 'simulation_runs'

    id = db.Column(db.BigInteger, primary_key=True)
    incident_id = db.Column(db.BigInteger, db.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False)
    scenario_name = db.Column(db.String(150))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_interruption_min = db.Column(db.Integer)
    continuity_risk = db.Column(db.String(30))
    recommendation = db.Column(db.Text)

    incident = db.relationship('Incident', backref=db.backref('simulation_runs', lazy=True))


class SimulationImpactEvent(db.Model):
    __tablename__ = 'simulation_impact_events'

    id = db.Column(db.BigInteger, primary_key=True)
    simulation_run_id = db.Column(db.BigInteger, db.ForeignKey('simulation_runs.id', ondelete='CASCADE'), nullable=False)
    minute_offset = db.Column(db.Integer, nullable=False)
    component_key = db.Column(db.String(100), nullable=False)
    impact_level = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, nullable=False)

    simulation_run = db.relationship('SimulationRun', backref=db.backref('impact_events', lazy=True))


class ReadinessQuestion(db.Model):
    __tablename__ = 'readiness_questions'

    id = db.Column(db.Integer, primary_key=True)
    question_key = db.Column(db.String(100), unique=True, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    weight = db.Column(db.Float, default=1.0)


class ReadinessAssessment(db.Model):
    __tablename__ = 'readiness_assessments'

    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(150))
    total_score = db.Column(db.Float)
    max_score = db.Column(db.Float)
    percentage_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ReadinessAnswer(db.Model):
    __tablename__ = 'readiness_answers'

    id = db.Column(db.BigInteger, primary_key=True)
    assessment_id = db.Column(db.BigInteger, db.ForeignKey('readiness_assessments.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('readiness_questions.id', ondelete='CASCADE'), nullable=False)
    answer_value = db.Column(db.String(30), nullable=False)
    numeric_score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)

    assessment = db.relationship('ReadinessAssessment', backref=db.backref('answers', lazy=True))
    question = db.relationship('ReadinessQuestion', backref=db.backref('answers', lazy=True))
