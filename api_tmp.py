import pandas as pd
import math
import random
from flask import Flask, request, jsonify
from utils import *
import os

# Charger les données
passenger_df = pd.read_csv("passenger_data.csv")
driver_df = pd.read_csv("driver_data.csv")

# Constantes des poids
w1, w2, w3 = 0.3, 0.2, 0.5

# Rayon de la Terre en kilomètres
EARTH_RADIUS = 6371.0

def haversine(lat1, lon1, lat2, lon2):
    """Calcule la distance de Haversine entre deux points géographiques."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS * c

def compute_relevance_score(passenger, driver):
    """Calcule le score de pertinence Sij."""
    # Distance entre passager et chauffeur
    distance = haversine(
        passenger['latitude'], passenger['longitude'],
        driver['latitude'], driver['longitude']
    )
    # Concordance des itinéraires (simulation ici)
    concordance = 1 if random.choice([True, False]) else 0
    # Score final
    score = w1 * (1 / (1 + distance)) + w2 * driver['rating'] + w3 * concordance
    return score

def assign_driver_to_passenger(passenger):
    """Assigne le chauffeur avec le score le plus élevé à un passager."""
    best_driver = None
    best_score = -1
    for _, driver in driver_df.iterrows():
        score = compute_relevance_score(passenger, driver)
        if score > best_score:
            best_driver = driver
            best_score = score
    return best_driver, best_score

def get_top_n_customers(driver_id, n):
    """Récupère les n premiers clients pour un chauffeur donné en fonction du score."""
    driver = driver_df[driver_df['driver_id'] == driver_id].iloc[0]
    passenger_scores = []

    for _, passenger in passenger_df.iterrows():
        score = compute_relevance_score(passenger, driver)
        passenger_scores.append((passenger['passenger_id'], score))

    passenger_scores.sort(key=lambda x: x[1], reverse=True)
    return passenger_scores[:n]

# Initialiser Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def welcome():
    """ACCUEIL"""
    
    return jsonify({"message": "Bienvenue sur l'api de recommandation des clients et chauffeurs pour l'application Ride and go."}), 200

@app.route("/assign_driver", methods=["POST"])
def assign_driver():
    """Endpoint pour assigner un chauffeur à un passager."""
    passenger_data = request.json
    passenger = pd.Series(passenger_data)
    best_driver, best_score = assign_driver_to_passenger(passenger)
    if best_driver is not None:
        return jsonify({
            "driver_id": best_driver['driver_id'],
            "score": best_score
        })
    return jsonify({"message": "Aucun chauffeur disponible."}), 404

@app.route("/top_customers/<driver_id>/<int:n>", methods=["GET"])
def top_customers(driver_id, n):
    """Endpoint pour récupérer les n premiers clients d'un chauffeur."""
    try:
        top_customers = get_top_n_customers(driver_id, n)
        return jsonify({"top_customers": top_customers})
    except IndexError:
        return jsonify({"message": "Chauffeur introuvable."}), 404


@app.route('/cost', methods=['POST'])
def cost():
    data = request.get_json()
    data = get_data(data.get('start'), data.get('end'),data.get('hour'))
    cost = calculate_cost(data)
    # return jsonify({'cost':cost})
    return f"{cost}"
    
def calculate_cost(data):
    return model.predict(data)

if __name__ == '__main__':
    app.run(debug=True)