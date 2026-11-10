# app.py - Flask backend API for INTEL-AIML_Rapido: Intelligent Mobility Insights
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "project": "INTEL-AIML_Rapido: Intelligent Mobility Insights",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({
        "message": "Data retrieved successfully",
        "project_id": "proj-intel-aiml-rapido-intelligent-mobility-insights",
        "status": "active"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
