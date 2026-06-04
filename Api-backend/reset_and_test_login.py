# reset_and_test_login.py
import sys
import os
import importlib.util
from werkzeug.security import generate_password_hash
import urllib.request
import json

spec = importlib.util.spec_from_file_location("app_root", "app.py")
root_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_app)

from dao.model import Usuario, db

# 1. Update Oswaldo's password in the database
with root_app.app.app_context():
    u = Usuario.query.filter_by(correo="Oswajesus.ma@gmail.com").first()
    if u:
        u.contrasena = generate_password_hash("admin123")
        db.session.commit()
        print("Password updated for Oswaldo successfully!")
    else:
        print("User Oswaldo not found.")
        sys.exit(1)

# 2. Call the login API to see what it returns
login_url = "http://127.0.0.1:5000/api/v1/auth/login"
data = json.dumps({"correo": "Oswajesus.ma@gmail.com", "contrasena": "admin123"}).encode('utf-8')
req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        print("API Login Response:")
        print(json.dumps(res_data, indent=2))
except Exception as e:
    print(f"Error calling login API: {e}")
