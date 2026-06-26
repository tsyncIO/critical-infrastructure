from collections import deque
from app.models import SimulationRun, SimulationImpactEvent, Incident, BcmProfile, InfrastructureComponent, InfrastructureDependency
from app.extensions import db

IMPACT_LEVELS = {
    0: 'severe',
    1: 'reduced',
    2: 'at_risk',
    3: 'monitoring_required',
}


def simulate_incident(incident_id: int, scenario_name: str = 'default') -> int:
    incident = Incident.query.get(incident_id)
    if not incident:
        raise ValueError('Incident not found')
    root = incident.root_cause_candidate
    paths = _collect_paths(root)
    interruption = 90 if incident.severity == 'critical' else 30
    interruption += 15 * len(paths)
    continuity_risk = 'high' if interruption > 60 else 'medium' if interruption > 30 else 'low'
    recommendation = _recommendation_for_component(root)
    sim = SimulationRun(
        incident_id=incident.id,
        scenario_name=scenario_name,
        estimated_interruption_min=interruption,
        continuity_risk=continuity_risk,
        recommendation=recommendation,
    )
    db.session.add(sim)
    db.session.flush()
    for depth, comp in enumerate([root] + paths):
        level = IMPACT_LEVELS.get(depth, 'monitoring_required')
        event = SimulationImpactEvent(
            simulation_run_id=sim.id,
            minute_offset=depth * 10,
            component_key=comp,
            impact_level=level,
            message=f"{comp} is {level} at minute {depth * 10} due to incident {incident.id}."
        )
        db.session.add(event)
    db.session.commit()
    return sim.id


def _collect_paths(component_key: str) -> list[str]:
    queue = deque([component_key])
    visited = {component_key}
    paths = []
    while queue:
        current = queue.popleft()
        deps = InfrastructureDependency.query.join(InfrastructureComponent, InfrastructureDependency.source_component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == current).all()
        for dep in deps:
            target = dep.target_component.component_key
            if target not in visited:
                visited.add(target)
                paths.append(target)
                queue.append(target)
    return paths


def _recommendation_for_component(component_key: str) -> str:
    profile = BcmProfile.query.join(InfrastructureComponent, BcmProfile.component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == component_key).first()
    if not profile:
        return 'No BCM profile available for this component.'
    return profile.recovery_action or 'Review BCM profile and respond accordingly.'
