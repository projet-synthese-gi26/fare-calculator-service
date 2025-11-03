import uuid
from flask import Flask, request, jsonify
from flasgger import Swagger
from utils import *
import os
import hashlib
import time
from flask_cors import CORS, cross_origin


port = int(os.environ.get("PORT", 5000))

DRIVERS_FILE = 'drivers.pkl'
PASSENGERS_FILE = 'passengers.pkl'

# Initialiser Flask
app = Flask(__name__)
Swagger(app)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://rideandgo.vercel.app"]}})

@app.route('/docs')
@cross_origin()
def swagger_ui():
    return redirect('/apidocs/') 


@app.route("/", methods=["GET"])
@cross_origin()
def welcome():
    """ACCUEIL"""
    return jsonify({"message": "Bienvenue sur l'api de recommandation des clients et chauffeurs pour l'application Ride and go."}), 200

# Stockage temporaire des tokens
active_sessions = {}

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    """
    Inscription d'un nouvel utilisateur.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
            - phone_number
            - first_name
            - last_name
            - birthdate
            - sex
            - role
          properties:
            username:
              type: string
              example: "johndoe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
            phone_number:
              type: string
              example: "+237691234567"
            first_name:
              type: string
              example: "John"
            last_name:
              type: string
              example: "Doe"
            birthdate:
              type: string
              example: "1995-06-15"
            sex:
              type: string
              enum: ["M", "F"]
              example: "M"
            role:
              type: string
              enum: ["driver", "passenger"]
              example: "driver"
    responses:
      200:
        description: Utilisateur enregistré avec succès
      400:
        description: Erreur dans les données fournies
    """
    data = request.get_json()
    role = data.get("role")

    if role not in ["driver", "passenger"]:
        return jsonify({"message": "Rôle invalide !"}), 400

    file_path = DRIVERS_FILE if role == "driver" else PASSENGERS_FILE
    users = load_data(file_path)

    if data["username"] in users:
        return jsonify({"message": "Cet utilisateur existe déjà"}), 400

    hashed_password = hashlib.sha256(data["password"].encode()).hexdigest()

    user = {
        "personal_info": {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password,
            "phone_number": data["phone_number"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "birthdate": data["birthdate"],
            "sex": data["sex"],
            "role": role
        },
        "localisation": {"longitude": None, "latitude": None},
    }

    if role == "driver":
        user.update({
            "rating": 0,
            "routes": []
        })
    else:
        user.update({
            "travel": {
                "start_lon": None, "start_lat": None,
                "end_lon": None, "end_lat": None
            }
        })

    users.append(user)
    save_data(file_path, users)

    return jsonify({"message": f"Utilisateur {role} enregistré avec succès"}), 200


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    """
    Connexion d'un utilisateur avec email, username ou téléphone.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - identifier
            - password
          properties:
            identifier:
              type: string
              example: "john@example.com"
              description: "Email, username ou numéro de téléphone"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Connexion réussie avec token
      401:
        description: Identifiants incorrects
    """
    data = request.get_json()
    identifier = data.get("identifier")  # Peut être email, username ou phone_number
    password = hashlib.sha256(data.get("password").encode()).hexdigest()

    # Charger les fichiers
    # users = {**load_data(DRIVERS_FILE), **load_data(PASSENGERS_FILE)}
    users = load_data(DRIVERS_FILE) + load_data(PASSENGERS_FILE)

    # Vérifier l'utilisateur avec email, username ou téléphone
    for user in users:
        personal_info = user["personal_info"]
        if identifier in [personal_info["email"], personal_info["username"], personal_info["phone_number"]]:
            if personal_info["password"] == password:
                # 🔹 Génération du token
                token = str(uuid.uuid4())  
                active_sessions[token] = user['personal_info']['username']  # 🔹 Stockage de la session
                
                return jsonify({
                    "message": "Connexion réussie",
                    "token": token,  # Le token est renvoyé ici
                    "role": personal_info["role"]  # 🔹 Info utile pour le frontend
                }), 200

    return jsonify({"message": "Identifiants incorrects"}), 401



@app.route('/set_localisation', methods=['POST'])
@cross_origin()
def set_localisation():
    """
    Mise à jour de la localisation d'un utilisateur.
    ---
    tags:
      - Utilisateur
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
            - longitude
            - latitude
          properties:
            token:
              type: string
              example: "c1247d5b-938f-4dfb-bfd7-8416b9c24b4a"
              description: "Token d'authentification de l'utilisateur"
            longitude:
              type: number
              example: 11.5234
              description: "Longitude de l'utilisateur"
            latitude:
              type: number
              example: 3.8765
              description: "Latitude de l'utilisateur"
    responses:
      200:
        description: Localisation mise à jour avec succès
      400:
        description: Requête invalide ou utilisateur non trouvé
      401:
        description: Token invalide
    """
    data = request.get_json()
    token = data.get("token")
    longitude = data.get("longitude")
    latitude = data.get("latitude")

    if token not in active_sessions:
        return jsonify({"message": "Token invalide"}), 401

    username = active_sessions[token]
    
    # Charger les fichiers
    drivers = load_data(DRIVERS_FILE)
    passengers = load_data(PASSENGERS_FILE)

    if username in drivers:
        users = drivers
        file_path = DRIVERS_FILE
    elif username in passengers:
        users = passengers
        file_path = PASSENGERS_FILE
    else:
        return jsonify({"message": "Utilisateur non trouvé"}), 400

    # Mettre à jour la localisation
    users[username]["localisation"] = {"longitude": longitude, "latitude": latitude}
    save_data(file_path, users)

    return jsonify({"message": "Localisation mise à jour avec succès"}), 200

@app.route('/get_localisation', methods=['GET'])
@cross_origin()
def get_localisation():
    """
    Récupérer les informations de localisation de l'utilisateur.
    ---
    tags:
      - Authentification
    parameters:
      - name: Authorization
        in: header
        required: true
        description: "Le token d'authentification de l'utilisateur"
        schema:
          type: string
    responses:
      200:
        description: Localisation récupérée avec succès
        schema:
          type: object
          properties:
            longitude:
              type: number
              example: 12.345
            latitude:
              type: number
              example: 54.321
      401:
        description: Token invalide ou manquant
      404:
        description: Localisation non trouvée
    """
    token = request.headers.get('Authorization')  # Récupérer le token de l'en-tête

    if not token:
        return jsonify({"message": "Token manquant"}), 401

    username = active_sessions.get(token)  # Vérifier si le token est valide

    if not username:
        return jsonify({"message": "Token invalide"}), 401

    # Charger les fichiers des utilisateurs
    users = {**load_data(DRIVERS_FILE), **load_data(PASSENGERS_FILE)}

    # Récupérer l'utilisateur associé au token
    user = users.get(username)
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    # Retourner les informations de localisation
    localisation = user.get("localisation")
    if not localisation:
        return jsonify({"message": "Localisation non trouvée"}), 404

    return jsonify(localisation), 200

@app.route('/set_routes', methods=['POST'])
@cross_origin()
def set_routes():
    """
    Permet à un conducteur de définir plusieurs de ses itinéraires.
    ---
    tags:
      - Conducteur
    parameters:
      - name: Authorization
        in: header
        required: true
        description: "Le token d'authentification de l'utilisateur"
        schema:
          type: string
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            routes:
              type: array
              items:
                type: object
                properties:
                  start:
                    type: string
                    example: "Point A"
                  end:
                    type: string
                    example: "Point B"
    responses:
      200:
        description: Routes mises à jour avec succès
      401:
        description: Token invalide ou manquant
      400:
        description: Mauvais format ou données invalides
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token manquant"}), 401

    username = active_sessions.get(token)
    if not username:
        return jsonify({"message": "Token invalide"}), 401

    # Charger les données
    users = load_data(DRIVERS_FILE)
    driver = users.get(username)

    if not driver or driver["personal_info"]["role"] != "driver":
        return jsonify({"message": "Utilisateur non conducteur"}), 401

    data = request.get_json()
    routes = data.get("routes")

    if not routes or not all("start" in route and "end" in route for route in routes):
        return jsonify({"message": "Données invalides"}), 400

    # Mettre à jour les routes du driver
    driver["routes"] = routes
    users[username] = driver
    save_data(DRIVERS_FILE, users)

    return jsonify({"message": "Routes mises à jour avec succès"}), 200


@app.route('/get_users', methods=['GET'])
@cross_origin()
def get_users():
    """
    Récupérer la liste des utilisateurs.
    ---
    tags:
      - Utilisateur
    responses:
      200:
        description: Liste des utilisateurs récupérée avec succès
        schema:
          type: array
          items:
            type: object
            properties:
              username:
                type: string
              email:
                type: string
              phone_number:
                type: string
              first_name:
                type: string
              last_name:
                type: string
              birthdate:
                type: string
              sex:
                type: string
              role:
                type: string
    """
    # Charger les fichiers des utilisateurs
    drivers = load_data(DRIVERS_FILE)
    passengers = load_data(PASSENGERS_FILE)

    # Fusionner les utilisateurs
    users = drivers + passengers

    # Extraire les informations pertinentes
    # user_list = [
    #     {
    #         "username": user["personal_info"]["username"],
    #         "email": user["personal_info"]["email"],
    #         "phone_number": user["personal_info"]["phone_number"],
    #         "first_name": user["personal_info"]["first_name"],
    #         "last_name": user["personal_info"]["last_name"],
    #         "birthdate": user["personal_info"]["birthdate"],
    #         "sex": user["personal_info"]["sex"],
    #         "role": user["personal_info"]["role"]
    #     }
    #     for user in users
    # ]

    return jsonify(users), 200


@app.route('/get_routes', methods=['GET'])
@cross_origin()
def get_routes():
    """
    Permet à un conducteur de récupérer ses itinéraires.
    ---
    tags:
      - Conducteur
    parameters:
      - name: Authorization
        in: header
        required: true
        description: "Le token d'authentification de l'utilisateur"
        schema:
          type: string
    responses:
      200:
        description: Routes récupérées avec succès
        schema:
          type: array
          items:
            type: object
            properties:
              start:
                type: string
                example: "Point A"
              end:
                type: string
                example: "Point B"
      401:
        description: Token invalide ou manquant
      404:
        description: Aucune route trouvée
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token manquant"}), 401

    username = active_sessions.get(token)
    if not username:
        return jsonify({"message": "Token invalide"}), 401

    # Charger les données
    users = load_data(DRIVERS_FILE)
    driver = users.get(username)

    if not driver or driver["personal_info"]["role"] != "driver":
        return jsonify({"message": "Utilisateur non conducteur"}), 401

    # Retourner les itinéraires du conducteur
    routes = driver.get("routes", [])

    if not routes:
        return jsonify({"message": "Aucune route trouvée"}), 404

    return jsonify(routes), 200


@app.route('/set_travel', methods=['POST'])
@cross_origin()
def set_travel():
    """
    Permet à un passager de définir ou de mettre à jour son itinéraire de voyage.
    ---
    tags:
      - Passager
    parameters:
      - name: Authorization
        in: header
        required: true
        description: "Le token d'authentification de l'utilisateur"
        schema:
          type: string
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            start_lon:
              type: number
              example: 12.345
            start_lat:
              type: number
              example: 54.321
            end_lon:
              type: number
              example: 14.567
            end_lat:
              type: number
              example: 55.432
    responses:
      200:
        description: Itinéraire de voyage mis à jour avec succès
      401:
        description: Token invalide ou manquant
      400:
        description: Mauvais format ou données invalides
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token manquant"}), 401

    username = active_sessions.get(token)
    if not username:
        return jsonify({"message": "Token invalide"}), 401

    # Charger les données
    users = load_data(PASSENGERS_FILE)
    passenger = users.get(username)

    if not passenger or passenger["personal_info"]["role"] != "passenger":
        return jsonify({"message": "Utilisateur non passager"}), 401

    data = request.get_json()
    start_lon = data.get("start_lon")
    start_lat = data.get("start_lat")
    end_lon = data.get("end_lon")
    end_lat = data.get("end_lat")

    if not (start_lon and start_lat and end_lon and end_lat):
        return jsonify({"message": "Données de localisation invalides"}), 400

    # Mettre à jour le voyage du passager
    passenger["travel"] = {
        "start_lon": start_lon,
        "start_lat": start_lat,
        "end_lon": end_lon,
        "end_lat": end_lat
    }
    users[username] = passenger
    save_data(PASSENGERS_FILE, users)

    return jsonify({"message": "Itinéraire de voyage mis à jour avec succès"}), 200

@app.route('/get_travel', methods=['GET'])
@cross_origin()
def get_travel():
    """
    Permet à un passager de récupérer son itinéraire de voyage.
    ---
    tags:
      - Passager
    parameters:
      - name: Authorization
        in: header
        required: true
        description: "Le token d'authentification de l'utilisateur"
        schema:
          type: string
    responses:
      200:
        description: Itinéraire de voyage récupéré avec succès
        schema:
          type: object
          properties:
            start_lon:
              type: number
              example: 12.345
            start_lat:
              type: number
              example: 54.321
            end_lon:
              type: number
              example: 14.567
            end_lat:
              type: number
              example: 55.432
      401:
        description: Token invalide ou manquant
      404:
        description: Itinéraire de voyage non trouvé
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token manquant"}), 401

    username = active_sessions.get(token)
    if not username:
        return jsonify({"message": "Token invalide"}), 401

    # Charger les données
    users = load_data(PASSENGERS_FILE)
    passenger = users.get(username)

    if not passenger or passenger["personal_info"]["role"] != "passenger":
        return jsonify({"message": "Utilisateur non passager"}), 401

    # Retourner l'itinéraire du passager
    travel = passenger.get("travel")

    if not travel:
        return jsonify({"message": "Itinéraire de voyage non trouvé"}), 404

    return jsonify(travel), 200



# @app.route("/assign_driver", methods=["POST"])
# def assign_driver():
#     """Endpoint pour assigner un chauffeur à un passager."""
#     passenger_data = request.json
#     passenger = pd.Series(passenger_data)
#     best_driver, best_score = assign_driver_to_passenger(passenger)
#     if best_driver is not None:
#         return jsonify({
#             "driver_id": best_driver['driver_id'],
#             "score": best_score
#         })
#     return jsonify({"message": "Aucun chauffeur disponible."}), 404

# @app.route("/top_customers/<driver_username>/<int:n>", methods=["GET"])
# def top_customers(driver_username, n):
#     """Endpoint pour récupérer les n premiers clients d'un chauffeur."""
#     try:
#         top_customers = get_top_n_customers(driver_username, n)
#         return jsonify({"top_customers": top_customers})
#     except IndexError:
#         return jsonify({"message": "Chauffeur introuvable."}), 404


# @app.route('/cost', methods=['POST'])
# def cost():
#     data = request.get_json()
#     data = get_data(data.get('start'), data.get('end'),data.get('hour'))
#     cost = calculate_cost(data)
#     # return jsonify({'cost':cost})
#     return f"{cost}"

@app.route("/top_customers/<driver_username>/<int:n>", methods=["GET"])
@cross_origin()
def top_customers(driver_username, n):
    """
    Récupère les N clients les plus fréquents d'un chauffeur spécifique.
    ---
    tags:
      - Statistiques Chauffeur
    parameters:
      - name: driver_username
        in: path
        type: string
        required: true
        description: Nom d'utilisateur du chauffeur
        example: "johndoe"
      - name: n
        in: path
        type: integer
        required: true
        description: Nombre de clients à retourner
        example: 5
    responses:
      200:
        description: Liste des N premiers clients
        schema:
          type: object
          properties:
            top_customers:
              type: array
              items:
                type: object
                properties:
                  username:
                    type: string
                  trip_count:
                    type: integer
      404:
        description: Chauffeur non trouvé
    """
    try:
        top_customers = get_top_n_customers(driver_username, n)
        return jsonify({"top_customers": top_customers})
    except IndexError:
        return jsonify({"message": "Chauffeur introuvable."}), 404


# # function to convert hour
# def map_hour_to_integer(hour):
#     if isinstance(hour, int):
#         # Si c'est déjà un entier entre 0 et 23, le retourner directement
#         if 0 <= hour <= 23:
#             return hour
#         else:
#             raise ValueError("L'heure doit être entre 0 et 23")
#     elif isinstance(hour, str):
#         # Si c'est une chaîne au format HH:MM, la convertir
#         try:
#             time_obj = datetime.strptime(hour, "%H:%M").time()
#             return time_obj.hour
#         except ValueError:
#             raise ValueError("Le format de l'heure doit être HH:MM")
        

@app.route('/cost', methods=['POST'])
@cross_origin()
def cost():
    """
    Calcule le coût estimé d'une course en fonction des paramètres fournis.
    ---
    tags:
      - Tarification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - start
            - end
            - hour
          properties:
            start:
              type: string
              description: Point de départ (nom du lieu ou adresse)
              example: "Yaoundé, Carrefour Warda"
            end:
              type: string
              description: Point d'arrivée (nom du lieu ou adresse)
              example: "Yaoundé, Poste Centrale"
            hour:
              type: string
              description: Heure de départ au format HH:MM
              example: "14:01"
    responses:
      200:
        description: Détails de la tarification
        schema:
          type: object
          properties:
            cost:
              type: number
              description: Coût estimé de la course
              example: 2500
            distance:
              type: number
              description: Distance entre les deux points en kilomètres
              example: 5.2
            start:
              type: string
              description: Point de départ
              example: "Yaoundé, Carrefour Warda"
            end:
              type: string
              description: Point d'arrivée
              example: "Yaoundé, Poste Centrale"
            mint_cost:
              type: number
              description: Coût minimum selon l'heure
              example: 350
      400:
        description: Données invalides ou manquantes
    """
    data = request.get_json()

    start = data.get('start')
    end = data.get('end')
    hour = data.get('hour')
    data = get_data(start, end, hour)

    start_lon, start_lat = get_coordinates(start)
    end_lon, end_lat = get_coordinates(end)
    distance = calculate_distance(start_lon, start_lat, end_lon, end_lat)
    cost = calculate_cost(data)

    # Convertir le coût en un type sérialisable JSON
    cost = cost.item() if hasattr(cost, 'item') else cost

    mint_cost = 350

    return jsonify({
      "cost": cost,
      "distance": distance,
      "start": start,
      "end": end,
      "mint_cost": mint_cost
    })

    
def calculate_cost(data):
    return model.predict(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=False)
