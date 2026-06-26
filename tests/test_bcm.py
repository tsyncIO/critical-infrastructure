"""test_bcm.py – Tests for BCM profile evaluation."""
import pytest
from app.models import InfrastructureComponent, BcmProfile
from app.services.bcm import evaluate_continuity_risk, get_bcm_profile


def _seed_bcm(db):
    comp = InfrastructureComponent(
        component_key='cooling_system_bcm',
        display_name='Cooling System (BCM test)',
    )
    db.session.add(comp)
    db.session.flush()
    profile = BcmProfile(
        component_id=comp.id,
        maximum_tolerable_downtime_min=60,
        recovery_time_objective_min=30,
        backup_available=True,
        backup_duration_min=45,
        recovery_action='Activate backup cooling.',
        emergency_contact_role='Technical operations lead',
    )
    db.session.add(profile)
    db.session.commit()
    return comp


def test_interruption_above_mtd_returns_high_risk(app, db):
    """Estimated interruption above MTD must return high continuity risk."""
    with app.app_context():
        _seed_bcm(db)
        result = evaluate_continuity_risk('cooling_system_bcm', interruption_min=90)
        assert result['continuity_risk'] == 'high'


def test_interruption_between_rto_and_mtd_returns_medium_risk(app, db):
    """Interruption between RTO (30) and MTD (60) must return medium risk."""
    with app.app_context():
        result = evaluate_continuity_risk('cooling_system_bcm', interruption_min=45)
        assert result['continuity_risk'] == 'medium'


def test_interruption_below_rto_returns_low_risk(app, db):
    """Interruption below RTO must return low risk."""
    with app.app_context():
        result = evaluate_continuity_risk('cooling_system_bcm', interruption_min=20)
        assert result['continuity_risk'] == 'low'


def test_bcm_profile_not_found_returns_unknown(app, db):
    """Missing BCM profile for a component must return unknown risk."""
    with app.app_context():
        result = evaluate_continuity_risk('nonexistent_component', interruption_min=100)
        assert result['continuity_risk'] == 'unknown'


def test_bcm_profile_lookup(app, db):
    """get_bcm_profile must return the BcmProfile for a known component."""
    with app.app_context():
        profile = get_bcm_profile('cooling_system_bcm')
        assert profile is not None
        assert profile.maximum_tolerable_downtime_min == 60
        assert profile.recovery_time_objective_min == 30
