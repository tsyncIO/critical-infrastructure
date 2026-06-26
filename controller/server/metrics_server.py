from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    print(f"[DEBUG] /metrics called -> cpu_percent={cpu}, memory_percent={memory}, disk_percent={disk}")

    return jsonify({
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_percent": disk
    })

@app.route("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)