from app.models import BcmProfile, InfrastructureComponent


def get_bcm_profile(component_key: str):
    return BcmProfile.query.join(InfrastructureComponent, BcmProfile.component_id == InfrastructureComponent.id).filter(InfrastructureComponent.component_key == component_key).first()


def evaluate_continuity_risk(component_key: str, interruption_min: int):
    profile = get_bcm_profile(component_key)
    if not profile:
        return {'continuity_risk': 'unknown', 'recommendation': 'No BCM profile found.'}
    if interruption_min > profile.maximum_tolerable_downtime_min:
        risk = 'high'
    elif interruption_min > profile.recovery_time_objective_min:
        risk = 'medium'
    else:
        risk = 'low'
    return {
        'continuity_risk': risk,
        'recommendation': profile.recovery_action,
        'backup_available': profile.backup_available,
        'backup_duration_min': profile.backup_duration_min,
    }
