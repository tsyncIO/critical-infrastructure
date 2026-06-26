from flask import Flask, jsonify
import psutil

app = Flask(__name__)


def _cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for entries in temps.values():
                if entries:
                    return entries[0].current
    except Exception:
        pass
    return 45.0


@app.route('/redfish/v1/')
def service_root():
    return jsonify({
        '@odata.type': '#ServiceRoot.v1_0_0.ServiceRoot',
        'Id': 'RootService',
        'Name': 'OpenBMC Redfish Service',
        'Systems': {'@odata.id': '/redfish/v1/Systems'},
        'Chassis': {'@odata.id': '/redfish/v1/Chassis'},
        'Sensors': {'@odata.id': '/redfish/v1/Sensors'}
    })


@app.route('/redfish/v1/Systems')
def systems():
    return jsonify({
        '@odata.type': '#ComputerSystemCollection.ComputerSystemCollection',
        'Name': 'Systems Collection',
        'Members': [{'@odata.id': '/redfish/v1/Systems/1'}],
        'Members@odata.count': 1
    })


@app.route('/redfish/v1/Systems/1')
def system_one():
    return jsonify({
        '@odata.type': '#ComputerSystem.v1_6_0.ComputerSystem',
        'Id': '1',
        'Name': 'Local System',
        'PowerState': 'On',
        'Status': {'State': 'Enabled', 'Health': 'OK'}
    })


@app.route('/redfish/v1/Chassis')
def chassis():
    return jsonify({
        '@odata.type': '#ChassisCollection.ChassisCollection',
        'Name': 'Chassis Collection',
        'Members': [{'@odata.id': '/redfish/v1/Chassis/1'}],
        'Members@odata.count': 1
    })


@app.route('/redfish/v1/Chassis/1')
def chassis_one():
    return jsonify({
        '@odata.type': '#Chassis.v1_8_0.Chassis',
        'Id': '1',
        'Name': 'Main Chassis',
        'Thermal': {'@odata.id': '/redfish/v1/Chassis/1/Thermal'},
        'Status': {'State': 'Enabled', 'Health': 'OK'}
    })


@app.route('/redfish/v1/Sensors')
def sensors():
    return jsonify({
        '@odata.type': '#SensorCollection.SensorCollection',
        'Name': 'Sensor Collection',
        'Members': [
            {
                '@odata.id': '/redfish/v1/Sensors/1',
                'Name': 'CPU Temperature',
                'ReadingType': 'Temperature',
                'Reading': _cpu_temp(),
                'Status': {'State': 'Enabled', 'Health': 'OK'}
            }
        ],
        'Members@odata.count': 1
    })


@app.route('/redfish/v1/health')
def health():
    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
