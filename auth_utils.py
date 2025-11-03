# auth_utils.py

from flask import request, jsonify

def verify_token():
    """
    Placeholder function to verify JWT.
    In a real-world scenario, this function would:
    1. Extract the token from the 'Authorization: Bearer <token>' header.
    2. Communicate with the central Authentication service to validate the token.
    3. Return the decoded token payload (e.g., containing user_id, roles, permissions).
    For now, it does nothing and returns a placeholder user ID.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        # This part can be activated later for real validation
        # return None, (jsonify({"message": "Authorization header is missing or invalid"}), 401)
        pass # For now, we let it pass

    # Placeholder logic
    print("--- verify_token called ---")
    print("NOTE: Token validation is currently disabled for development.")
    print("-------------------------")
    
    # Simulating a successful token verification
    mock_user_id = "user-id-from-a-valid-jwt"
    return mock_user_id, None # (user_id, error_response)