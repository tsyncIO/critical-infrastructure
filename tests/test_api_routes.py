import json
from app.models import RawDatasetFile, TepRun, SensorVariable, VariableStatistic, AlarmEvent, InfrastructureComponent, InfrastructureDependency, ReadinessQuestion


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_bpmn_metadata_endpoint(client):
    response = client.get('/api/bpmn')
    assert response.status_code == 200
    assert 'viewer_url' in response.json
    assert response.json['title'] == 'Crisis response BPMN model'


def test_bpmn_xml_endpoint(client):
    response = client.get('/api/bpmn/xml')
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert '<bpmn:definitions' in response.get_data(as_text=True)


def test_dependency_graph_endpoint(client, db):
    comp1 = InfrastructureComponent(component_key='a', display_name='A')
    comp2 = InfrastructureComponent(component_key='b', display_name='B')
    db.session.add_all([comp1, comp2])
    db.session.commit()
    dep = InfrastructureDependency(source_component_id=comp1.id, target_component_id=comp2.id, dependency_type='test', criticality='medium')
    db.session.add(dep)
    db.session.commit()

    response = client.get('/api/dependencies/graph')
    assert response.status_code == 200
    payload = response.json
    assert 'nodes' in payload and 'edges' in payload
    assert any(node['id'] == 'a' for node in payload['nodes'])
    assert any(edge['source'] == 'a' and edge['target'] == 'b' for edge in payload['edges'])


def test_alarms_endpoint_structure(client, db):
    file = RawDatasetFile(file_name='test.RData', file_path='Data/test.RData', dataset_role='faulty_testing')
    db.session.add(file)
    db.session.flush()
    run = TepRun(dataset_file_id=file.id, run_id='role-0-0', dataset_role='faulty_testing', fault_id=1, fault_label='fault_1', is_faulty=True, row_count=1, variable_count=1)
    db.session.add(run)
    db.session.flush()
    variable = SensorVariable(variable_name='xmeas_test', component_key='industrial_process')
    db.session.add(variable)
    db.session.flush()
    stat = VariableStatistic(variable_id=variable.id, warning_low=0, warning_high=1, critical_low=-1, critical_high=2)
    db.session.add(stat)
    db.session.flush()
    alarm = AlarmEvent(run_id=run.id, observation_id=None, time_step=1, variable_id=variable.id, component_key='industrial_process', alarm_type='warning_high_alarm', severity='warning', message='test', deviation_value=0.5, threshold_value=1.0)
    db.session.add(alarm)
    db.session.commit()

    response = client.get('/api/alarms')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(item['alarm_type'] == 'warning_high_alarm' for item in response.json)
