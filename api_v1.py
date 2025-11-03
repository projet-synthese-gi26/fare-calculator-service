# api_v1.py

from flask import Blueprint, request, jsonify
from utils import get_data, calculate_cost, calculate_distance, get_coordinates
from auth_utils import verify_token

v1_blueprint = Blueprint('v1', __name__)

# --- API Endpoints compliant with the v1.0 Contract ---

@v1_blueprint.route('/fares/calculate', methods=['POST'])
def calculate_fare():
    """
    Calculate estimated fare for a trip
    ---
    tags:
      - Fares
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: FareCalculationRequest
          required:
            - startLocationName
            - endLocationName
            - departureTime
          properties:
            startLocationName:
              type: string
              example: "Carrefour Warda"
            endLocationName:
              type: string
              example: "Mvog-Mbi"
            departureTime:
              type: string
              example: "19:30"
    responses:
      200:
        description: Fare calculation successful
        schema:
          id: FareEstimate
          properties:
            estimatedFare:
              type: integer
              example: 450
            officialFare:
              type: integer
              example: 300
            distanceInKm:
              type: number
              example: 5.2
            startLocationName:
              type: string
              example: "Carrefour Warda"
            endLocationName:
              type: string
              example: "Mvog-Mbi"
      400:
        description: Bad request - missing required fields
      500:
        description: Internal server error
    """
    data = request.get_json()
    start_name = data.get('startLocationName')
    end_name = data.get('endLocationName')
    time = data.get('departureTime')

    if not all([start_name, end_name, time]):
        return jsonify({
            "timestamp": "2025-11-03T10:00:00.000Z",
            "status": 400,
            "error": "Bad Request",
            "message": "startLocationName, endLocationName, and departureTime are required.",
            "path": "/api/v1/fares/calculate"
        }), 400

    try:
        # Reuse existing logic from utils.py
        prediction_data = get_data(start_name, end_name, time)
        estimated_fare_result = calculate_cost(prediction_data)
        
        # Ensure the fare is a standard number
        fare_value = float(estimated_fare_result[0]) if hasattr(estimated_fare_result, '__iter__') else float(estimated_fare_result)

        # Get coordinates to calculate distance
        start_lon, start_lat = get_coordinates(start_name)
        end_lon, end_lat = get_coordinates(end_name)

        if start_lon is None or end_lon is None:
             return jsonify({
                "timestamp": "2025-11-03T10:01:00.000Z",
                "status": 400,
                "error": "Bad Request",
                "message": "Could not geocode one of the locations. Please provide valid location names.",
                "path": "/api/v1/fares/calculate"
            }), 400

        distance_km = calculate_distance(start_lon, start_lat, end_lon, end_lat)

        # Format the response according to the contract
        response = {
            "estimatedFare": round(fare_value),
            "officialFare": 300,  # Placeholder value
            "distanceInKm": round(distance_km, 2),
            "startLocationName": start_name,
            "endLocationName": end_name
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "timestamp": "2025-11-03T10:02:00.000Z",
            "status": 500,
            "error": "Internal Server Error",
            "message": f"An unexpected error occurred: {str(e)}",
            "path": "/api/v1/fares/calculate"
        }), 500

@v1_blueprint.route('/fares/submit-actual', methods=['POST'])
def submit_actual_fare():
    """
    Submit actual completed trip fare
    ---
    tags:
      - Fares
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            startLocationName:
              type: string
            endLocationName:
              type: string
            actualFare:
              type: integer
            departureTime:
              type: string
    responses:
      201:
        description: Fare data recorded successfully
      401:
        description: Unauthorized - invalid or missing token
    """
    user_id, error = verify_token()
    if error:
        return error

    data = request.get_json()
    # In a real app, you would save this data to a database or a file for model retraining
    print(f"User '{user_id}' submitted actual fare data: {data}")
    
    return jsonify({"message": "Fare data recorded successfully."}), 201

@v1_blueprint.route('/itineraries/me', methods=['GET'])
def get_itineraries():
    """
    Get saved itineraries for authenticated user
    ---
    tags:
      - Itineraries
    security:
      - Bearer: []
    responses:
      200:
        description: List of user's saved itineraries
        schema:
          type: array
          items:
            id: Itinerary
            properties:
              id:
                type: string
                example: "iti_a1b2c3d4e5f6"
              startLocationName:
                type: string
                example: "Mvog-Ada"
              endLocationName:
                type: string
                example: "École de Police"
              savedFare:
                type: integer
                example: 250
      401:
        description: Unauthorized - invalid or missing token
    """
    user_id, error = verify_token()
    if error:
        return error

    # In a real app, you would fetch itineraries for 'user_id' from a database
    print(f"Fetching itineraries for user '{user_id}'...")
    
    # Mock response compliant with the contract
    mock_itineraries = [
      {
        "id": "iti_a1b2c3d4e5f6",
        "startLocationName": "Mvog-Ada",
        "endLocationName": "École de Police",
        "savedFare": 250
      },
      {
        "id": "iti_b2c3d4e5f6g7",
        "startLocationName": "Ngoa-Ekélé, Cité U",
        "endLocationName": "Poste Centrale",
        "savedFare": 300
      }
    ]
    return jsonify(mock_itineraries), 200

@v1_blueprint.route('/itineraries/me', methods=['POST'])
def save_itineraries():
    """
    Save or update itineraries for authenticated user
    ---
    tags:
      - Itineraries
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            itineraries:
              type: array
              items:
                type: object
                properties:
                  startLocationName:
                    type: string
                  endLocationName:
                    type: string
                  savedFare:
                    type: integer
    responses:
      200:
        description: Itineraries updated successfully
      401:
        description: Unauthorized - invalid or missing token
    """
    user_id, error = verify_token()
    if error:
        return error
    
    data = request.get_json()
    itineraries_to_save = data.get('itineraries')
    
    # In a real app, you would save this list of itineraries to the database, associated with 'user_id'
    print(f"Saving itineraries for user '{user_id}': {itineraries_to_save}")
    
    return jsonify({"message": "Itineraries updated successfully."}), 200