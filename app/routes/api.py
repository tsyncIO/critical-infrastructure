from flask import Blueprint, jsonify, request, url_for, current_app, Response
from app.models import (
    RawDatasetFile,
    TepRun,
    SensorVariable,
    AlarmEvent,
    Incident,
    InfrastructureComponent,
    InfrastructureDependency,
    ReadinessQuestion,
    ReadinessAssessment,
    ReadinessAnswer,
    SimulationRun,
    SimulationImpactEvent,
)
from app.services.simulator import simulate_incident
from app.services.readiness_score import score_assessment
from app.services.dependency_analyzer import get_downstream_impacts, calculate_dependency_risk

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'kritis-alarm-lab'})


@api_bp.route('/dataset/summary')
def dataset_summary():
    return jsonify({
        'files_loaded': RawDatasetFile.query.count(),
        'runs': TepRun.query.count(),
        'variables': SensorVariable.query.count(),
        'alarms': AlarmEvent.query.count(),
        'incidents': Incident.query.count(),
        'simulations': SimulationRun.query.count(),
        'readiness_assessments': ReadinessAssessment.query.count(),
    })


@api_bp.route('/files')
def files():
    return jsonify([{
        'id': f.id,
        'file_name': f.file_name,
        'dataset_role': f.dataset_role,
        'loaded_at': f.loaded_at.isoformat(),
    } for f in RawDatasetFile.query.order_by(RawDatasetFile.loaded_at.desc()).all()])


@api_bp.route('/runs')
def runs():
    return jsonify([{
        'id': run.id,
        'run_id': run.run_id,
        'dataset_role': run.dataset_role,
        'fault_label': run.fault_label,
        'is_faulty': run.is_faulty,
    } for run in TepRun.query.order_by(TepRun.id.desc()).limit(200).all()])


@api_bp.route('/variables')
def variables():
    return jsonify([{
        'id': v.id,
        'variable_name': v.variable_name,
        'component_key': v.component_key,
    } for v in SensorVariable.query.order_by(SensorVariable.variable_name).limit(200).all()])


@api_bp.route('/alarms')
def alarms():
    query = AlarmEvent.query
    role = request.args.get('role')
    if role:
        query = query.join(TepRun).filter(TepRun.dataset_role == role)
    alarms = query.order_by(AlarmEvent.created_at.desc()).limit(200).all()
    return jsonify([{
        'id': a.id,
        'run_id': a.run_id,
        'time_step': a.time_step,
        'component_key': a.component_key,
        'alarm_type': a.alarm_type,
        'severity': a.severity,
        'message': a.message,
        'duplicate': a.is_duplicate,
        'threshold_value': a.threshold_value,
        'deviation_value': a.deviation_value,
    } for a in alarms])


@api_bp.route('/incidents')
def incidents():
    incidents = Incident.query.order_by(Incident.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': i.id,
        'title': i.title,
        'severity': i.severity,
        'status': i.status,
        'raw_alarm_count': i.raw_alarm_count,
        'unique_alarm_count': i.unique_alarm_count,
        'explanation': i.explanation,
        'first_time_step': i.first_time_step,
        'last_time_step': i.last_time_step,
        'created_at': i.created_at.isoformat(),
    } for i in incidents])


@api_bp.route('/incidents/<int:incident_id>')
def incident_detail(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    alarms = [
        {
            'id': link.alarm_event.id,
            'time_step': link.alarm_event.time_step,
            'component_key': link.alarm_event.component_key,
            'alarm_type': link.alarm_event.alarm_type,
            'severity': link.alarm_event.severity,
            'message': link.alarm_event.message,
        }
        for link in incident.incident_alarm_events
    ]
    return jsonify({
        'id': incident.id,
        'title': incident.title,
        'severity': incident.severity,
        'status': incident.status,
        'raw_alarm_count': incident.raw_alarm_count,
        'unique_alarm_count': incident.unique_alarm_count,
        'affected_component_count': incident.affected_component_count,
        'explanation': incident.explanation,
        'alarms': alarms,
    })


@api_bp.route('/incidents/<int:incident_id>/simulate', methods=['POST'])
def simulate_incident_route(incident_id):
    """Create a cascading impact simulation for the given incident."""
    incident = Incident.query.get_or_404(incident_id)
    scenario_name = (request.json or {}).get('scenario_name', 'default')
    try:
        sim_id = simulate_incident(incident_id, scenario_name=scenario_name)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404
    sim = SimulationRun.query.get(sim_id)
    impacts = [
        {
            'minute_offset': ev.minute_offset,
            'component_key': ev.component_key,
            'impact_level': ev.impact_level,
            'message': ev.message,
        }
        for ev in sim.impact_events
    ]
    return jsonify({
        'simulation_id': sim.id,
        'incident_id': incident_id,
        'scenario_name': sim.scenario_name,
        'estimated_interruption_min': sim.estimated_interruption_min,
        'continuity_risk': sim.continuity_risk,
        'recommendation': sim.recommendation,
        'impacts': impacts,
    }), 201


@api_bp.route('/components')
def components():
    return jsonify([{
        'id': c.id,
        'key': c.component_key,
        'display_name': c.display_name,
        'sector': c.sector,
        'responsible_org': c.responsible_org,
        'description': c.description,
    } for c in InfrastructureComponent.query.order_by(InfrastructureComponent.display_name).all()])


@api_bp.route('/dependencies')
def dependencies():
    dependencies = InfrastructureDependency.query.all()
    return jsonify([{
        'id': d.id,
        'source': d.source_component.component_key,
        'target': d.target_component.component_key,
        'dependency_type': d.dependency_type,
        'criticality': d.criticality,
        'description': d.description,
    } for d in dependencies])


@api_bp.route('/dependencies/impact/<string:component_key>')
def dependency_impact(component_key):
    """Return downstream impact analysis for a given component."""
    comp = InfrastructureComponent.query.filter_by(component_key=component_key).first()
    if not comp:
        return jsonify({'error': f'Component {component_key!r} not found'}), 404
    severity = request.args.get('severity', 'critical')
    downstream = get_downstream_impacts(component_key)
    risk_result = calculate_dependency_risk(component_key, severity)
    return jsonify({
        'component_key': component_key,
        'display_name': comp.display_name,
        'incident_severity': severity,
        'downstream_components': downstream,
        'risk': risk_result['risk'],
        'impact_paths': risk_result['impacts'],
    })


@api_bp.route('/dependencies/graph')
def dependency_graph():
    nodes = []
    edges = []
    components = {c.id: c for c in InfrastructureComponent.query.all()}
    for comp in components.values():
        nodes.append({'id': comp.component_key, 'label': comp.display_name, 'sector': comp.sector})
    for dep in InfrastructureDependency.query.all():
        edges.append({
            'id': f'{dep.source_component_id}_{dep.target_component_id}',
            'source': dep.source_component.component_key,
            'target': dep.target_component.component_key,
            'criticality': dep.criticality,
            'dependency_type': dep.dependency_type,
        })
    return jsonify({'nodes': nodes, 'edges': edges})


@api_bp.route('/simulations')
def simulations():
    sims = SimulationRun.query.order_by(SimulationRun.started_at.desc()).limit(100).all()
    return jsonify([{
        'id': s.id,
        'incident_id': s.incident_id,
        'scenario_name': s.scenario_name,
        'estimated_interruption_min': s.estimated_interruption_min,
        'continuity_risk': s.continuity_risk,
        'recommendation': s.recommendation,
        'started_at': s.started_at.isoformat(),
    } for s in sims])


@api_bp.route('/simulations/<int:simulation_id>')
def simulation_detail(simulation_id):
    sim = SimulationRun.query.get_or_404(simulation_id)
    impacts = [
        {
            'minute_offset': ev.minute_offset,
            'component_key': ev.component_key,
            'impact_level': ev.impact_level,
            'message': ev.message,
        }
        for ev in sim.impact_events
    ]
    return jsonify({
        'id': sim.id,
        'incident_id': sim.incident_id,
        'scenario_name': sim.scenario_name,
        'estimated_interruption_min': sim.estimated_interruption_min,
        'continuity_risk': sim.continuity_risk,
        'recommendation': sim.recommendation,
        'impacts': impacts,
    })


@api_bp.route('/readiness/questions')
def readiness_questions():
    questions = ReadinessQuestion.query.order_by(ReadinessQuestion.category, ReadinessQuestion.question_key).all()
    return jsonify([{
        'id': q.id,
        'question_key': q.question_key,
        'question_text': q.question_text,
        'category': q.category,
        'weight': q.weight,
    } for q in questions])


@api_bp.route('/readiness/assessments')
def readiness_assessments():
    assessments = ReadinessAssessment.query.order_by(ReadinessAssessment.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'total_score': a.total_score,
        'max_score': a.max_score,
        'percentage_score': a.percentage_score,
        'created_at': a.created_at.isoformat(),
        'answers': [
            {
                'question_key': ans.question.question_key,
                'answer_value': ans.answer_value,
                'numeric_score': ans.numeric_score,
                'comment': ans.comment,
            }
            for ans in a.answers
        ],
    } for a in assessments])


@api_bp.route('/readiness/assess', methods=['POST'])
def readiness_assess():
    """Submit a new readiness assessment and return the scored result."""
    payload = request.get_json(silent=True)
    if not payload or 'answers' not in payload:
        return jsonify({'error': 'Request body must be JSON with an "answers" list'}), 400
    title = payload.get('title', 'Readiness Assessment')
    answers = payload['answers']  # list of {question_key, answer_value, comment?}
    assessment = score_assessment(answers, title=title)
    return jsonify({
        'id': assessment.id,
        'title': assessment.title,
        'total_score': assessment.total_score,
        'max_score': assessment.max_score,
        'percentage_score': assessment.percentage_score,
        'created_at': assessment.created_at.isoformat(),
    }), 201


@api_bp.route('/bpmn')
def bpmn_metadata():
    return jsonify({
        'viewer_url': url_for('static', filename='bpmn/crisis_response.bpmn', _external=False),
        'title': 'Crisis response BPMN model',
    })


@api_bp.route('/bpmn/xml')
def bpmn_xml():
    file_path = current_app.static_folder + '/bpmn/crisis_response.bpmn'
    try:
        with open(file_path, 'r', encoding='utf-8') as handle:
            xml = handle.read()
        return Response(xml, mimetype='application/xml')
    except FileNotFoundError:
        return jsonify({'error': 'BPMN file not found'}), 404
