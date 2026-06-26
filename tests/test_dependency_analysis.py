"""test_dependency_analysis.py – Tests for the dependency graph traversal."""
import pytest
from app.models import InfrastructureComponent, InfrastructureDependency
from app.services.dependency_analyzer import (
    get_direct_impacts,
    get_downstream_impacts,
    calculate_dependency_risk,
)


def _seed_kritis_components(db):
    """Seed a minimal KRITIS dependency chain for testing (idempotent)."""
    keys = [
        'emergency_power', 'process_control_system', 'cooling_system',
        'industrial_process', 'port_operations', 'municipal_crisis_coordination',
        'communication_system',
    ]
    comps = {}
    for k in keys:
        existing = InfrastructureComponent.query.filter_by(component_key=k).first()
        if existing:
            comps[k] = existing
        else:
            c = InfrastructureComponent(component_key=k, display_name=k.replace('_', ' ').title())
            db.session.add(c)
            comps[k] = c
    db.session.flush()

    deps = [
        ('emergency_power', 'process_control_system', 'high'),
        ('process_control_system', 'cooling_system', 'high'),
        ('cooling_system', 'industrial_process', 'high'),
        ('industrial_process', 'port_operations', 'medium'),
        ('port_operations', 'municipal_crisis_coordination', 'medium'),
        ('communication_system', 'municipal_crisis_coordination', 'high'),
    ]
    for src, tgt, crit in deps:
        exists = InfrastructureDependency.query.filter_by(
            source_component_id=comps[src].id,
            target_component_id=comps[tgt].id,
        ).first()
        if not exists:
            d = InfrastructureDependency(
                source_component_id=comps[src].id,
                target_component_id=comps[tgt].id,
                dependency_type='test',
                criticality=crit,
            )
            db.session.add(d)
    db.session.commit()
    return comps


def test_direct_impacts_from_cooling_system(app, db):
    """cooling_system directly impacts industrial_process."""
    with app.app_context():
        _seed_kritis_components(db)
        impacts = get_direct_impacts('cooling_system')
        assert 'industrial_process' in impacts


def test_downstream_impacts_from_cooling_system_includes_crisis_coord(app, db):
    """Downstream from cooling_system must include industrial_process, port_operations, and municipal_crisis_coordination."""
    with app.app_context():
        _seed_kritis_components(db)
        impacts = get_downstream_impacts('cooling_system')
        assert 'industrial_process' in impacts
        assert 'port_operations' in impacts
        assert 'municipal_crisis_coordination' in impacts


def test_dependency_risk_critical_incident_high_path_returns_high(app, db):
    """critical severity + high criticality dependency path → high risk."""
    with app.app_context():
        _seed_kritis_components(db)
        result = calculate_dependency_risk('cooling_system', 'critical')
        assert result['risk'] == 'high'


def test_dependency_risk_warning_incident_returns_medium_or_low(app, db):
    """warning severity + high criticality path → at least medium risk."""
    with app.app_context():
        _seed_kritis_components(db)
        result = calculate_dependency_risk('cooling_system', 'warning')
        assert result['risk'] in ('medium', 'high')
