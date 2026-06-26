from flask import Blueprint, render_template
from app.models import (
    TepRun,
    AlarmEvent,
    Incident,
    SimulationRun,
    ReadinessAssessment,
    ReadinessQuestion,
    InfrastructureComponent,
    InfrastructureDependency,
)
from .utils import get_overview_summary

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    summary = get_overview_summary()
    return render_template('index.html', summary=summary)


@pages_bp.route('/alarms')
def alarms():
    alarms = AlarmEvent.query.order_by(AlarmEvent.created_at.desc()).limit(200).all()
    return render_template('alarms.html', alarms=alarms)


@pages_bp.route('/incidents')
def incidents():
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return render_template('incidents.html', incidents=incidents)


@pages_bp.route('/dependencies')
def dependencies():
    components = InfrastructureComponent.query.order_by(InfrastructureComponent.display_name).all()
    dependencies = InfrastructureDependency.query.order_by(InfrastructureDependency.id).all()
    return render_template('dependencies.html', components=components, dependencies=dependencies)


@pages_bp.route('/simulation')
def simulation():
    simulations = SimulationRun.query.order_by(SimulationRun.started_at.desc()).limit(20).all()
    return render_template('simulation.html', simulations=simulations)


@pages_bp.route('/readiness')
def readiness():
    questions = ReadinessQuestion.query.order_by(ReadinessQuestion.category, ReadinessQuestion.question_key).all()
    latest = ReadinessAssessment.query.order_by(ReadinessAssessment.created_at.desc()).first()
    return render_template('readiness.html', questions=questions, latest=latest)


@pages_bp.route('/bpmn')
def bpmn():
    return render_template('bpmn.html')
