import pickle

# Chemin vers les fichiers binaires
DRIVER_DATA_FILE = 'driver_data.pkl'
PASSENGER_DATA_FILE = 'passenger_data.pkl'

# Fonction pour charger les données depuis un fichier binaire
def load_data(file_path):
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}  # Retourner un dictionnaire vide si le fichier n'existe pas

# Fonction pour sauvegarder les données dans un fichier binaire
def save_data(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

# Fonction pour ajouter ou mettre à jour un chauffeur dans le fichier binaire
def add_or_update_driver(driver_id, driver_info):
    # Charger les données existantes des chauffeurs
    drivers_data = load_data(DRIVER_DATA_FILE)
    
    # Ajouter ou mettre à jour les informations du chauffeur
    drivers_data[driver_id] = driver_info
    
    # Sauvegarder les données mises à jour
    save_data(DRIVER_DATA_FILE, drivers_data)
    return {"message": "Chauffeur ajouté ou mis à jour avec succès."}

# Fonction pour ajouter ou mettre à jour un passager dans le fichier binaire
def add_or_update_passenger(passenger_id, passenger_info):
    # Charger les données existantes des passagers
    passengers_data = load_data(PASSENGER_DATA_FILE)
    
    # Ajouter ou mettre à jour les informations du passager
    passengers_data[passenger_id] = passenger_info
    
    # Sauvegarder les données mises à jour
    save_data(PASSENGER_DATA_FILE, passengers_data)
    return {"message": "Passager ajouté ou mis à jour avec succès."}

# Exemple d'utilisation
# Ajouter ou mettre à jour un chauffeur
driver_info = {
    'latitude': 4.0603,
    'longitude': 9.7085,
    'rating': 4.7,
    'routes': ['Route1', 'Route2']
}
response_driver = add_or_update_driver('driver123', driver_info)
print(response_driver)

# Ajouter ou mettre à jour un passager
passenger_info = {
    'latitude': 4.0583,
    'longitude': 9.7105,
    'departure_lat': 4.0600,
    'departure_long': 9.7100,
    'arrival_lat': 4.0550,
    'arrival_long': 9.7050
}
response_passenger = add_or_update_passenger('passenger456', passenger_info)
print(response_passenger)
p= load_data(PASSENGER_DATA_FILE)
print(p)
passenger_info2 = {
    'latitude': 4.0583,
    'longitude': 9.7105,
    'departure_lat': 4.0600,
    'departure_long': 9.7100,
    'arrival_lat': 4.0550,
    'arrival_long': 10.7050
}
response_passenger = add_or_update_passenger('passenger456', passenger_info2)
p= load_data(PASSENGER_DATA_FILE)

print(p)