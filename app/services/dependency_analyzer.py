from collections import deque
from app.models import InfrastructureDependency, InfrastructureComponent


def get_direct_impacts(component_key: str) -> list[str]:
    deps = InfrastructureDependency.query.join(InfrastructureComponent, InfrastructureDependency.source_component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == component_key).all()
    return [dep.target_component.component_key for dep in deps]


def get_downstream_impacts(component_key: str) -> list[str]:
    visited = set()
    queue = deque([component_key])
    results = []
    while queue:
        current = queue.popleft()
        for dep in InfrastructureDependency.query.join(InfrastructureComponent, InfrastructureDependency.source_component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == current).all():
            target = dep.target_component.component_key
            if target not in visited:
                visited.add(target)
                results.append(target)
                queue.append(target)
    return results


def get_impact_path(component_key: str) -> list[dict]:
    paths = []
    queue = deque([(component_key, [component_key])])
    while queue:
        current, path = queue.popleft()
        for dep in InfrastructureDependency.query.join(InfrastructureComponent, InfrastructureDependency.source_component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == current).all():
            next_key = dep.target_component.component_key
            new_path = path + [next_key]
            paths.append({'path': new_path, 'criticality': dep.criticality})
            queue.append((next_key, new_path))
    return paths


def calculate_dependency_risk(component_key: str, incident_severity: str) -> dict:
    impacts = get_impact_path(component_key)
    risk = 'low'
    for path in impacts:
        if incident_severity == 'critical' and path['criticality'] == 'high':
            risk = 'high'
            break
        if incident_severity == 'critical' and path['criticality'] == 'medium':
            risk = 'medium'
        if incident_severity == 'warning' and path['criticality'] == 'high' and risk != 'high':
            risk = 'medium'
    return {'component_key': component_key, 'incident_severity': incident_severity, 'risk': risk, 'impacts': impacts}
