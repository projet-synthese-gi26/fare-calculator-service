"""Functions used by the api"""

import joblib
from geopy.distance import geodesic
import requests
from datetime import datetime
import pickle
import math
import random
import pandas as pd


# Chemin vers les fichiers binaires
DRIVER_DATA_FILE = 'drivers.pkl'
PASSENGER_DATA_FILE = 'passengers.pkl'

# Fonction pour charger les données depuis un fichier binaire
def load_data(file_path):
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []  # Retourner un dictionnaire vide si le fichier n'existe pas

# Fonction pour sauvegarder les données dans un fichier binaire
def save_data(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
        
drivers = load_data(DRIVER_DATA_FILE)
passengers = load_data(PASSENGER_DATA_FILE)

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
        passenger['travel']['start_lat'], passenger['travel']['start_lon'],
        driver['localisation']['longitude'], driver['localisation']['latitude']
    )
    # Concordance des itinéraires (simulation ici)
    concordance = 1 if random.choice([True, False]) else 0
    # Score final
    score = w1 * (1 / (1 + distance)) + w2 * driver['rating'] + w3 * concordance
    return score

# def assign_driver_to_passenger(passenger):
#     """Assigne le chauffeur avec le score le plus élevé à un passager."""
#     best_driver = None
#     best_score = -1
#     for _, driver in driver_df.iterrows():
#         score = compute_relevance_score(passenger, driver)
#         if score > best_score:
#             best_driver = driver
#             best_score = score
#     return best_driver, best_score

def get_top_n_customers(driver_id, n):
    """Récupère les n premiers clients pour un chauffeur donné en fonction du score."""
    print(drivers)
    driver = next((d for d in drivers if d['personal_info']['username'] == driver_id), None)
    if driver is None:
        raise ValueError(f"No driver found with username {driver_id}")
    passenger_scores = []
    
    for passenger in passengers:
        score = compute_relevance_score(passenger, driver)
        passenger_scores.append((passenger['passenger_id'], score))

    passenger_scores.sort(key=lambda x: x[1], reverse=True)
    return passenger_scores[:n]

model = joblib.load('random_forests.pkl')

def calculate_cost(data):
    return model.predict(data)

def calculate_distance(lon_dep, lat_dep, lon_arr, lat_arr):
    return geodesic((lon_dep, lat_dep), (lon_arr, lat_arr)).kilometers

# Fonction pour obtenir les coordonnées à partir d'un quartier
def get_coordinates(neighborhood, city="Yaoundé", country="Cameroon"):
    address = f"{neighborhood}, {city}, {country}"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        "User-Agent":"RIdeAndGo/1..0{tresoeleroyd@gmail.com}"
    }
    response = requests.get(url, params=params, headers=headers)
    print(response.status_code)
    if response.status_code == 200 and response.json():
        print(response.text)
        data = response.json()[0]
        return float(data["lon"]), float(data["lat"])  # Renvoie (longitude, latitude)
    else:
        return None, None

def map_hour_to_integer(hour_str):
    """
    Mappe une heure au format HH:MM à un entier selon le mapping donné.

    :param hour_str: Une heure sous forme de chaîne de caractères (ex : "14:30").
    :return: L'entier correspondant au créneau horaire ou None si l'heure est invalide.
    """
    from datetime import datetime

    # Définir le mapping des créneaux horaires
    hour_mapping = {
        ("00:00", "04:59"): 1,
        ("05:00", "06:59"): 2,
        ("07:00", "08:59"): 3,
        ("09:00", "13:59"): 4,
        ("14:00", "15:29"): 5,
        ("15:30", "18:59"): 6,
        ("19:00", "21:00"): 7,
        ("21:01", "23:59"): 8,
    }

    try:
        # Convertir l'heure en objet datetime
        time_obj = datetime.strptime(hour_str, "%H:%M").time()

        # Parcourir le mapping pour trouver le créneau correspondant
        for (start, end), value in hour_mapping.items():
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()

            if start_time <= time_obj <= end_time:
                return value

    except ValueError:
        # Si l'heure est invalide
        print("Format d'heure invalide. Veuillez utiliser HH:MM.")

    return None

def get_data(start_p, end_p, hour=None):
    if hour is None:
        hour=datetime.now().strftime("%H:%M")
    lon_dep, lat_dep = get_coordinates(start_p)
    lon_arr, lat_arr = get_coordinates(end_p)
    distance = calculate_distance(lon_dep, lat_dep, lon_arr, lat_arr)
    hour = map_hour_to_integer(hour)
    if hour is None:
        raise ValueError(f"Impossible de mapper l'heure {hour}. Format attendu : HH:MM.")
    data = [[lon_dep, lat_dep, lon_arr, lat_arr, distance, hour]]
    return data