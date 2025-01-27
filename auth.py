import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/home/anand/Documents/mypropertyqr-gis-dash-firebase-adminsdk-fbsvc-d7d63f33e4.json")
firebase_admin.initialize_app(cred)

def revoke_user_tokens(uid):
    try:
        # Revoke the user's refresh tokens
        auth.revoke_refresh_tokens(uid)
        print(f"Refresh tokens for user {uid} have been revoked.")
    except Exception as e:
        print(f"Error revoking tokens: {e}")


def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        # Check if the token was issued after the refresh tokens were revoked
        revocation_time = auth.get_user(decoded_token['uid']).tokens_valid_after_timestamp / 1000
        if decoded_token['auth_time'] < revocation_time:
            raise Exception("Token has been revoked")
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None
    

def verify(tkn):
    user = verify_id_token(tkn)
    if user:
        # revoke_user_tokens(user['uid'])
        return True
    else:
        return False