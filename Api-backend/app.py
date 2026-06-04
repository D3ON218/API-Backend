from app import create_app
from dao.model import inicializar_db  
from routes.api_routes import api_bp
from flask_cors import CORS

app = create_app()

# Habilitar CORS en toda la aplicación para permitir peticiones desde Angular (localhost:4200)
CORS(app)

# Inicializar base de datos
inicializar_db(app)  

# Registrar blueprints
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(debug=True)
    