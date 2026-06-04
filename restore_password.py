# restore_password.py
import sys
import os
import importlib.util

spec = importlib.util.spec_from_file_location("app_root", "app.py")
root_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_app)

from dao.model import Usuario, db

original_hash = "scrypt:32768:8:1$AtPRU118dYtJY9Rr$349b1213506f0cb06ebac2af641102e58da2e5f502849b1ec35361b12ae8556ffce90cf073735eac70535d1b447d72416bc973f96ec00a1096180d61a88cea72"

with root_app.app.app_context():
    u = Usuario.query.filter_by(correo="Oswajesus.ma@gmail.com").first()
    if u:
        u.contrasena = original_hash
        db.session.commit()
        print("Restored original password hash successfully!")
    else:
        print("User not found.")
