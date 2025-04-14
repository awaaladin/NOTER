from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = 'your-secret-key'  # Same as your app's SECRET_KEY
SALT = 'email-confirm-salt'

def generate_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SALT)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SALT, max_age=expiration)
    except Exception:
        return False
    return email
