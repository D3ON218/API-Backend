# Backend API REST - Taller de Transmisiones Automáticas Zamora

Este directorio contiene el Backend del sistema de administración del Taller de Transmisiones Automáticas, desarrollado en **Flask (Python)** y utilizando **MySQL** como gestor de base de datos. Se ha expuesto una API REST completa para que pueda ser consumida por el Frontend desarrollado en Angular.

---

## Requisitos Previos

Asegúrate de tener instalados los siguientes componentes en tu sistema:
- **Python 3.10 o superior**
- **MySQL Server** (y opcionalmente MySQL Workbench)
- **Node.js** (para ejecutar el frontend de Angular)

---

## Instrucciones de Despliegue del Backend

Sigue los siguientes pasos para levantar el servidor local del Backend:

### 1. Preparación del Entorno Virtual (Python)

Si estás configurando el proyecto por primera vez o en una nueva PC, recrea el entorno virtual para evitar conflictos de rutas locales:

En la terminal (dentro de la carpeta `progra_web_isc_5_u3_taller_transmisiones_automaticas`):
```bash
# Recrear el entorno virtual
python -m venv venv

# Activar el entorno virtual (Windows)
.\venv\Scripts\activate

# Instalar dependencias requeridas
pip install flask flask-sqlalchemy pymysql mysql-connector-python flask-cors
```

### 2. Configuración de la Base de Datos MySQL

1. Inicia **MySQL Workbench** o tu cliente MySQL preferido.
2. Abre y ejecuta los scripts de base de datos en el siguiente orden para crear las tablas y poblar los datos semilla:
   - `1.-Tables.sql`
   - `2.-AlterTables.sql`
   - `3.-DatosPrueba.sql`
3. Si cambiaste la contraseña de tu usuario `root` de MySQL, actualiza la cadena de conexión en el archivo [config.py](config.py):
   ```python
   SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:TU_CONTRASEÑA@localhost/transmisiones_automaticas_zamora"
   ```

### 3. Ejecución del Servidor Backend

Con el entorno virtual activo y la base de datos levantada, ejecuta el archivo principal:
```bash
python app.py
```
El servidor de desarrollo iniciará por defecto en `http://localhost:5000`.

---

## Catálogo de Endpoints de la API REST (v1)

Todos los endpoints REST responden en formato **JSON** y aceptan solicitudes CORS desde `http://localhost:4200` (Angular).

### 👥 1. Usuarios (`/api/v1/usuarios`)
- `GET /api/v1/usuarios`: Obtiene todos los usuarios.
- `GET /api/v1/usuarios/<id>`: Obtiene detalles de un usuario específico.
- `POST /api/v1/usuarios`: Registra un nuevo usuario.
- `PUT /api/v1/usuarios/<id>`: Actualiza los datos de un usuario.
- `DELETE /api/v1/usuarios/<id>`: Elimina un usuario (si no tiene relaciones activas).

### 🚗 2. Vehículos/Coches (`/api/v1/coches`)
- `GET /api/v1/coches`: Obtiene todos los vehículos registrados junto con el nombre del propietario.
- `GET /api/v1/coches/<id>`: Obtiene un vehículo específico.
- `POST /api/v1/coches`: Asocia y registra un nuevo vehículo a un cliente.
- `PUT /api/v1/coches/<id>`: Edita datos de un vehículo (marca, modelo, año, placa, etc.).
- `DELETE /api/v1/coches/<id>`: Elimina un coche.

### 🔧 3. Servicios (`/api/v1/servicios`)
- `GET /api/v1/servicios`: Lista de servicios y costos estimados.
- `GET /api/v1/servicios/<id>`: Obtiene detalles de un servicio.
- `POST /api/v1/servicios`: Registra un nuevo tipo de servicio en el catálogo.
- `PUT /api/v1/servicios/<id>`: Edita un servicio existente.
- `DELETE /api/v1/servicios/<id>`: Remueve un servicio.

### 📅 4. Citas (`/api/v1/citas`)
- `GET /api/v1/citas`: Obtiene la agenda completa de citas.
- `GET /api/v1/citas/<id>`: Obtiene detalles de una cita.
- `POST /api/v1/citas`: Agenda una nueva cita asociando cliente, vehículo, fecha, hora y motivo.
- `PUT /api/v1/citas/<id>`: Re-programa o cambia el estado de la cita (`pendiente`, `confirmada`, `terminada`, `cancelada`).
- `DELETE /api/v1/citas/<id>`: Cancela/elimina una cita.

### 📋 5. Historial de Mantenimientos (`/api/v1/historial`)
- `GET /api/v1/historial`: Obtiene todos los registros de trabajos terminados con su costo e información de cliente/vehículo.
- `GET /api/v1/historial/<id>`: Obtiene un registro individual.
- `POST /api/v1/historial`: Agrega una orden de mantenimiento finalizada.
- `PUT /api/v1/historial/<id>`: Modifica kilometraje, costos o notas.
- `DELETE /api/v1/historial/<id>`: Elimina un registro de historial.

### 🌐 6. Simulación Northwind (`/api/v1/northwind/products`)
- `GET /api/v1/northwind/products`: Retorna refacciones de transmisión simulando el catálogo Northwind para integración externa.
