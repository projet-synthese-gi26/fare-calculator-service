# app.py
from flask import Flask, jsonify
from flasgger import Swagger
from flask_cors import CORS
import os
from api_v1 import v1_blueprint

# --- App Initialization ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Blueprint Registration (AVANT Swagger!) ---
app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

# --- Swagger Configuration ---
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "info": {
        "title": "TraEnSys - Fare Calculator API (v1.0)",
        "description": "API for fare estimation and itinerary management.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"]
}

Swagger(app, config=swagger_config, template=swagger_template)

# --- Root Endpoint ---
@app.route("/", methods=["GET"])
def welcome():
    return jsonify({
        "message": "Welcome to the TraEnSys Fare Calculator Service.",
        "documentation": "/apidocs/"
    }), 200

# --- Main Execution ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)