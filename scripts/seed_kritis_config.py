import json
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models import InfrastructureComponent, InfrastructureDependency, BcmProfile, ReadinessQuestion

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / '..' / 'kritis' / 'configs'


def load_config(filename):
    path = (CONFIG_DIR / filename).resolve()
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def main():
    app = create_app()
    with app.app_context():
        components = {c.component_key: c for c in InfrastructureComponent.query.all()}
        for comp in load_config('infrastructure_components.json'):
            if comp['component_key'] not in components:
                record = InfrastructureComponent(**comp)
                db.session.add(record)
        db.session.commit()

        components = {c.component_key: c for c in InfrastructureComponent.query.all()}
        for dep in load_config('infrastructure_dependencies.json'):
            source = components[dep['source']]
            target = components[dep['target']]
            exists = InfrastructureDependency.query.filter_by(source_component_id=source.id, target_component_id=target.id).first()
            if not exists:
                record = InfrastructureDependency(
                    source_component_id=source.id,
                    target_component_id=target.id,
                    dependency_type=dep['dependency_type'],
                    criticality=dep['criticality'],
                    description=dep['description'],
                )
                db.session.add(record)
        db.session.commit()

        components = {c.component_key: c for c in InfrastructureComponent.query.all()}
        for profile in load_config('bcm_profiles.json'):
            comp = components[profile['component_key']]
            exists = BcmProfile.query.filter_by(component_id=comp.id).first()
            if not exists:
                record = BcmProfile(
                    component_id=comp.id,
                    maximum_tolerable_downtime_min=profile['maximum_tolerable_downtime_min'],
                    recovery_time_objective_min=profile['recovery_time_objective_min'],
                    backup_available=profile['backup_available'],
                    backup_duration_min=profile['backup_duration_min'],
                    recovery_action=profile['recovery_action'],
                    emergency_contact_role=profile['emergency_contact_role'],
                )
                db.session.add(record)
        db.session.commit()

        for q in load_config('readiness_questions.json'):
            exists = ReadinessQuestion.query.filter_by(question_key=q['question_key']).first()
            if not exists:
                record = ReadinessQuestion(**q)
                db.session.add(record)
        db.session.commit()
        print('KRITIS configuration seeded.')


if __name__ == '__main__':
    main()
