import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "supersecretkey"

    # Conexión a la base de datos usando mysql-connector
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:*M1m0ku3m0kuj3l0*@localhost/transmisiones_automaticas_zamora"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Prevenir conexiones muertas en el pool (MySQL cierra conexiones inactivas)
    SQLALCHEMY_POOL_RECYCLE = 300       # Reciclar conexiones cada 5 minutos
    SQLALCHEMY_POOL_PRE_PING = True     # Verificar conexión antes de usarla
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    }

    # Configuración para subir archivos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
