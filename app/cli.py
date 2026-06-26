import json
import click
from pathlib import Path

from app.services.alarm_generator import generate_alarms_for_run
from app.services.alarm_filter import mark_duplicate_alarms
from app.services.incident_grouper import group_incidents
from app.services.simulator import simulate_incident
from app.services.readiness_score import score_assessment
from app.models import Incident


@click.group(name='kritis')
def kritis_cli():
    """KRITIS Alarm & Dependency Lab commands."""
    pass


@kritis_cli.command('inspect-tep')
def inspect_tep():
    """Inspect raw Tennessee Eastman Process data files."""
    import scripts.inspect_tep_rdata as inspect_tep_rdata
    inspect_tep_rdata.main()


@kritis_cli.command('init-db')
def init_db():
    """Create application database tables."""
    import scripts.init_db as init_db_script
    init_db_script.main()


@kritis_cli.command('ingest-tep')
def ingest_tep():
    """Preprocess and ingest TEP dataset files."""
    import scripts.preprocess_tep as preprocess_tep_script
    preprocess_tep_script.ingest()


@kritis_cli.command('seed-configs')
def seed_configs():
    """Seed synthetic KRITIS infrastructure and BCM configuration."""
    import scripts.seed_kritis_config as seed_kritis_script
    seed_kritis_script.main()


@kritis_cli.command('generate-alarms')
@click.option('--role', default=None, help='Filter by dataset role.')
@click.option('--run-id', default=None, help='Filter by a specific run identifier.')
@click.option('--limit', default=0, type=int, help='Limit the number of observations processed.')
def generate_alarms(role, run_id, limit):
    """Generate alarm events from ingested TEP observations."""
    count = generate_alarms_for_run(run_id=run_id, dataset_role=role, limit=limit)
    click.echo(f'Generated {count} alarm events.')


@kritis_cli.command('filter-alarms')
@click.option('--window', default=3, type=int, help='Duplicate window size in time steps.')
def filter_alarms(window):
    """Mark duplicate alarms within a sliding time window."""
    count = mark_duplicate_alarms(window=window)
    click.echo(f'Filtered and updated {count} alarm events.')


@kritis_cli.command('group-incidents')
@click.option('--window-size', default=10, type=int, help='Severity grouping window size in time steps.')
def group_incidents_cmd(window_size):
    """Group filtered alarms into incident records."""
    count = group_incidents(window_size=window_size)
    click.echo(f'Created {count} incidents from filtered alarms.')


@kritis_cli.command('run-simulation')
@click.option('--incident-id', default=None, type=int, help='Incident ID to simulate. Uses the latest incident if omitted.')
def run_simulation(incident_id):
    """Run a cascading impact simulation for an incident."""
    if incident_id is None:
        latest_incident = Incident.query.order_by(Incident.created_at.desc()).first()
        if latest_incident is None:
            click.echo('No incidents available; run group-incidents first.')
            return
        incident_id = latest_incident.id
    sim_id = simulate_incident(incident_id)
    click.echo(f'Created simulation run {sim_id}.')


@kritis_cli.command('assess-readiness')
@click.option('--answers-file', default=None, type=click.Path(exists=True), help='JSON file with readiness answers.')
def assess_readiness(answers_file):
    """Score a readiness assessment from a JSON file."""
    if answers_file:
        with open(answers_file, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    else:
        payload = [
            {'question_key': 'dependencies_documented', 'answer_value': 'yes'},
            {'question_key': 'backup_power_available', 'answer_value': 'partial'},
            {'question_key': 'alternative_communication_available', 'answer_value': 'yes'},
        ]
    assessment = score_assessment(payload)
    click.echo(f'Created readiness assessment {assessment.id} with {assessment.percentage_score:.1f}% score.')
