from app import create_app
from app.services.simulator import simulate_incident
from app.models import Incident


def main():
    app = create_app()
    with app.app_context():
        incident = Incident.query.order_by(Incident.created_at.desc()).first()
        if not incident:
            print('No incidents found. Run group_incidents first.')
            return
        sim_id = simulate_incident(incident.id, scenario_name='sample_kritis_simulation')
        print(f'Created simulation run {sim_id} for incident {incident.id}.')


if __name__ == '__main__':
    main()
