import hashlib
import base64

def generate_rabbitmq_password_hash(password):
    salt = "somesalt"  # Use a consistent salt
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).digest()
    base64_encoded_hash = base64.b64encode(hashed_password).decode('utf-8')
    return base64_encoded_hash

password = "password"
print(generate_rabbitmq_password_hash(password))
