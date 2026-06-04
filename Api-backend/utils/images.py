import os
from werkzeug.utils import secure_filename
from config import Config

def save_image(file, folder):
    if not file or file.filename == "":
        return None

    if not Config.allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    upload_path = os.path.join(Config.UPLOAD_FOLDER, folder)

    os.makedirs(upload_path, exist_ok=True)

    filepath = os.path.join(upload_path, filename)
    file.save(filepath)

    return f"uploads/{folder}/{filename}"

def delete_image(path):
    if not path:
        return

    if not path.startswith('static/'):
        full_path = os.path.join('static', path)
    else:
        full_path = path

    if os.path.exists(full_path):
        os.remove(full_path)