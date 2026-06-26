"""
kritis.db.seed_static_configs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seed static configuration data (infrastructure components, dependencies,
BCM profiles, readiness questions) from JSON files in kritis/configs/.

This is the canonical seeding script for KRITIS domain configuration.
It is idempotent: running it multiple times will not create duplicate records.

Usage:
    python -m kritis.db.seed_static_configs
"""
from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import (
    InfrastructureComponent,
    InfrastructureDependency,
    BcmProfile,
    ReadinessQuestion,
)

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = ROOT / "kritis" / "configs"


def _load(filename: str) -> list | dict:
    path = (CONFIG_DIR / filename).resolve()
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def seed_components() -> int:
    """Seed InfrastructureComponent records. Returns count of new records added."""
    existing = {c.component_key for c in InfrastructureComponent.query.all()}
    added = 0
    for comp in _load("infrastructure_components.json"):
        if comp["component_key"] not in existing:
            db.session.add(InfrastructureComponent(**comp))
            added += 1
    db.session.commit()
    print(f"  components: {added} added ({len(existing)} already present)")
    return added


def seed_dependencies() -> int:
    """Seed InfrastructureDependency records. Returns count of new records added."""
    components = {c.component_key: c for c in InfrastructureComponent.query.all()}
    added = 0
    for dep in _load("infrastructure_dependencies.json"):
        source = components[dep["source"]]
        target = components[dep["target"]]
        exists = InfrastructureDependency.query.filter_by(
            source_component_id=source.id,
            target_component_id=target.id,
        ).first()
        if not exists:
            record = InfrastructureDependency(
                source_component_id=source.id,
                target_component_id=target.id,
                dependency_type=dep["dependency_type"],
                criticality=dep["criticality"],
                description=dep.get("description", ""),
            )
            db.session.add(record)
            added += 1
    db.session.commit()
    print(f"  dependencies: {added} added")
    return added


def seed_bcm_profiles() -> int:
    """Seed BcmProfile records. Returns count of new records added."""
    components = {c.component_key: c for c in InfrastructureComponent.query.all()}
    added = 0
    for profile in _load("bcm_profiles.json"):
        comp = components[profile["component_key"]]
        exists = BcmProfile.query.filter_by(component_id=comp.id).first()
        if not exists:
            record = BcmProfile(
                component_id=comp.id,
                maximum_tolerable_downtime_min=profile["maximum_tolerable_downtime_min"],
                recovery_time_objective_min=profile["recovery_time_objective_min"],
                backup_available=profile["backup_available"],
                backup_duration_min=profile.get("backup_duration_min", 0),
                recovery_action=profile["recovery_action"],
                emergency_contact_role=profile["emergency_contact_role"],
            )
            db.session.add(record)
            added += 1
    db.session.commit()
    print(f"  BCM profiles: {added} added")
    return added


def seed_readiness_questions() -> int:
    """Seed ReadinessQuestion records. Returns count of new records added."""
    existing = {q.question_key for q in ReadinessQuestion.query.all()}
    added = 0
    for q in _load("readiness_questions.json"):
        if q["question_key"] not in existing:
            db.session.add(ReadinessQuestion(**q))
            added += 1
    db.session.commit()
    print(f"  readiness questions: {added} added")
    return added


def main() -> None:
    app = create_app()
    with app.app_context():
        print("Seeding KRITIS static configuration …")
        seed_components()
        seed_dependencies()
        seed_bcm_profiles()
        seed_readiness_questions()
        print("Done.")


if __name__ == "__main__":
    main()
