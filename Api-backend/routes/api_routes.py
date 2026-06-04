# routes/api_routes.py
from flask import Blueprint, request, jsonify
from dao.model import db, Usuario, Coche, Servicio, Cita, HistorialMantenimiento, TipoCita, DetalleServicio
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash

api_bp = Blueprint('api_bp', __name__, url_prefix='/api/v1')

# Asegurar que cada petición inicie con una sesión limpia de la BD
@api_bp.before_app_request
def refresh_session():
    """Elimina datos en caché de la sesión para que cada petición lea datos frescos de MySQL."""
    try:
        db.session.expire_all()
    except Exception:
        pass

# Cerrar la sesión de la BD al terminar cada petición para devolver la conexión al pool
@api_bp.teardown_app_request
def shutdown_session(exception=None):
    try:
        if exception:
            db.session.rollback()
        db.session.remove()
    except Exception:
        pass

# Helper to format responses
def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code

# Helper parsers
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_time(time_str):
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return None

# =========================================================================
# AUTHENTICATION ENDPOINTS
# =========================================================================
@api_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or {}
    correo = (data.get('correo') or '').strip()
    contrasena = (data.get('contrasena') or '').strip()

    if not correo or not contrasena:
        return error_response("Correo y contraseña son requeridos")

    user = Usuario.query.filter(db.func.lower(Usuario.correo) == correo.lower()).first()
    if user and check_password_hash(user.contrasena, contrasena):
        return jsonify({
            "id_usuario": user.id_usuario,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "correo": user.correo,
            "rol": user.rol,
            "foto": user.foto
        }), 200
    else:
        return error_response("Correo o contraseña incorrectos", 401)

@api_bp.route('/auth/registro', methods=['POST'])
def auth_registro():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    apellido = (data.get('apellido') or '').strip()
    correo = (data.get('correo') or '').strip()
    telefono = (data.get('telefono') or '').strip() or None
    contrasena = (data.get('contrasena') or '').strip()

    if not nombre or not correo or not contrasena:
        return error_response("Nombre, correo y contraseña son requeridos")

    if len(contrasena) < 8:
        return error_response("La contraseña debe tener al menos 8 caracteres")

    if Usuario.query.filter(db.func.lower(Usuario.correo) == correo.lower()).first():
        return error_response("El correo ya está registrado")

    hashed_pw = generate_password_hash(contrasena)

    try:
        nuevo = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            contrasena=hashed_pw,
            rol='cliente'  # Rol forzado siempre como cliente
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_usuario": nuevo.id_usuario,
            "nombre": nuevo.nombre,
            "correo": nuevo.correo,
            "rol": nuevo.rol
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/auth/cambiar_contrasena', methods=['POST'])
def auth_cambiar_contrasena():
    data = request.get_json() or {}
    id_usuario = data.get('id_usuario')
    contrasena_actual = data.get('contrasena_actual', '').strip()
    nueva_contrasena = data.get('nueva_contrasena', '').strip()

    if not id_usuario or not contrasena_actual or not nueva_contrasena:
        return error_response("Campos requeridos: id_usuario, contrasena_actual, nueva_contrasena")

    if len(nueva_contrasena) < 8:
        return error_response("La nueva contraseña debe tener al menos 8 caracteres")

    user = Usuario.query.get(id_usuario)
    if not user or not check_password_hash(user.contrasena, contrasena_actual):
        return error_response("La contraseña actual es incorrecta", 401)

    try:
        user.contrasena = generate_password_hash(nueva_contrasena)
        db.session.commit()
        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


# =========================================================================
# 1. USUARIOS CRUD
# =========================================================================
@api_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    try:
        usuarios = Usuario.query.all()
        return jsonify([{
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "correo": u.correo,
            "telefono": u.telefono,
            "rol": u.rol,
            "foto": u.foto
        } for u in usuarios]), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error GET /usuarios: {e}")
        return error_response(f"Error al consultar usuarios: {str(e)}", 500)

@api_bp.route('/usuarios/<int:id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    u = Usuario.query.get(id_usuario)
    if not u:
        return error_response("Usuario no encontrado", 404)
    return jsonify({
        "id_usuario": u.id_usuario,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "correo": u.correo,
        "telefono": u.telefono,
        "rol": u.rol,
        "foto": u.foto
    }), 200

@api_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    apellido = (data.get('apellido') or '').strip()
    correo = (data.get('correo') or '').strip()
    telefono = (data.get('telefono') or '').strip() or None
    contrasena = (data.get('contrasena') or '').strip()
    # Rol forzado como cliente, no se permite elegir admin desde los formularios
    rol = 'cliente'
    foto = (data.get('foto') or '').strip() or None

    if not nombre or not correo:
        return error_response("Nombre y Correo son requeridos")

    # Check if user already exists
    if Usuario.query.filter(db.func.lower(Usuario.correo) == correo.lower()).first():
        return error_response("El correo ya está registrado")

    hashed_pw = generate_password_hash(contrasena) if contrasena else generate_password_hash("default123")

    try:
        nuevo = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            contrasena=hashed_pw,
            rol=rol,
            foto=foto
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_usuario": nuevo.id_usuario,
            "nombre": nuevo.nombre,
            "correo": nuevo.correo,
            "rol": nuevo.rol
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def update_usuario(id_usuario):
    u = Usuario.query.get(id_usuario)
    if not u:
        return error_response("Usuario no encontrado", 404)

    data = request.get_json() or {}
    if 'nombre' in data: u.nombre = (data['nombre'] or '').strip()
    if 'apellido' in data: u.apellido = (data['apellido'] or '').strip()
    if 'correo' in data:
        new_correo = (data['correo'] or '').strip()
        if new_correo != u.correo and Usuario.query.filter(db.func.lower(Usuario.correo) == new_correo.lower()).first():
            return error_response("El correo ya está registrado")
        u.correo = new_correo
    if 'telefono' in data: u.telefono = (data['telefono'] or '').strip() or None
    # No permitimos modificar el rol a través del API para que solo se haga por base de datos
    # if 'rol' in data: u.rol = (data['rol'] or '').strip()
    if 'foto' in data: u.foto = (data['foto'] or '').strip() or None
    if 'contrasena' in data and data['contrasena']:
        u.contrasena = generate_password_hash((data['contrasena'] or '').strip())

    try:
        db.session.commit()
        return jsonify({
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "correo": u.correo,
            "rol": u.rol,
            "foto": u.foto,
            "telefono": u.telefono
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


@api_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def delete_usuario(id_usuario):
    u = Usuario.query.get(id_usuario)
    if not u:
        return error_response("Usuario no encontrado", 404)
    try:
        # Borrar en cascada manual de registros dependientes si es necesario
        db.session.delete(u)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error (es posible que tenga coches o citas asociadas): {str(e)}", 500)


# =========================================================================
# 2. COCHES CRUD
# =========================================================================
@api_bp.route('/coches', methods=['GET'])
def get_coches():
    try:
        coches = Coche.query.all()
        res = []
        for c in coches:
            u = Usuario.query.get(c.id_usuario)
            res.append({
                "id_coche": c.id_coche,
                "id_usuario": c.id_usuario,
                "nombre_usuario": f"{u.nombre} {u.apellido}" if u else "Desconocido",
                "marca": c.marca,
                "modelo": c.modelo,
                "anio": c.anio,
                "placa": c.placa,
                "foto": c.foto
            })
        return jsonify(res), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error GET /coches: {e}")
        return error_response(f"Error al consultar coches: {str(e)}", 500)

@api_bp.route('/coches/<int:id_coche>', methods=['GET'])
def get_coche(id_coche):
    c = Coche.query.get(id_coche)
    if not c:
        return error_response("Coche no encontrado", 404)
    u = Usuario.query.get(c.id_usuario)
    return jsonify({
        "id_coche": c.id_coche,
        "id_usuario": c.id_usuario,
        "nombre_usuario": f"{u.nombre} {u.apellido}" if u else "Desconocido",
        "marca": c.marca,
        "modelo": c.modelo,
        "anio": c.anio,
        "placa": c.placa,
        "foto": c.foto
    }), 200

@api_bp.route('/coches', methods=['POST'])
def create_coche():
    data = request.get_json() or {}
    id_usuario = data.get('id_usuario')
    marca = (data.get('marca') or '').strip()
    modelo = (data.get('modelo') or '').strip()
    anio = data.get('anio')
    placa = (data.get('placa') or '').strip()
    foto = (data.get('foto') or '').strip()

    id_usuario = int(id_usuario) if id_usuario else None

    if not id_usuario or not marca or not modelo or not placa:
        return error_response("Campos requeridos: id_usuario, marca, modelo, placa")

    if not Usuario.query.get(id_usuario):
        return error_response("El usuario asociado no existe")

    try:
        nuevo = Coche(
            id_usuario=id_usuario,
            marca=marca,
            modelo=modelo,
            anio=int(anio) if anio else None,
            placa=placa,
            foto=foto
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_coche": nuevo.id_coche,
            "marca": nuevo.marca,
            "modelo": nuevo.modelo,
            "placa": nuevo.placa
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/coches/<int:id_coche>', methods=['PUT'])
def update_coche(id_coche):
    c = Coche.query.get(id_coche)
    if not c:
        return error_response("Coche no encontrado", 404)

    data = request.get_json() or {}
    if 'id_usuario' in data:
        val_usuario = int(data['id_usuario']) if data['id_usuario'] else None
        if not val_usuario or not Usuario.query.get(val_usuario):
            return error_response("El usuario asociado no existe")
        c.id_usuario = val_usuario
    if 'marca' in data: c.marca = (data['marca'] or '').strip()
    if 'modelo' in data: c.modelo = (data['modelo'] or '').strip()
    if 'anio' in data: c.anio = int(data['anio']) if data['anio'] is not None and data['anio'] != '' else None
    if 'placa' in data: c.placa = (data['placa'] or '').strip()
    if 'foto' in data: c.foto = (data['foto'] or '').strip()

    try:
        db.session.commit()
        return jsonify({
            "id_coche": c.id_coche,
            "id_usuario": c.id_usuario,
            "marca": c.marca,
            "modelo": c.modelo,
            "placa": c.placa
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/coches/<int:id_coche>', methods=['DELETE'])
def delete_coche(id_coche):
    c = Coche.query.get(id_coche)
    if not c:
        return error_response("Coche no encontrado", 404)
    try:
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Coche eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


# =========================================================================
# 3. SERVICIOS CRUD
# =========================================================================
@api_bp.route('/servicios', methods=['GET'])
def get_servicios():
    try:
        servicios = Servicio.query.all()
        return jsonify([{
            "id_servicio": s.id_servicio,
            "nombre": s.nombre,
            "descripcion": s.descripcion,
            "precio_aprox": s.precio_aprox,
            "imagen": s.imagen
        } for s in servicios]), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error GET /servicios: {e}")
        return error_response(f"Error al consultar servicios: {str(e)}", 500)

@api_bp.route('/servicios/<int:id_servicio>', methods=['GET'])
def get_servicio(id_servicio):
    s = Servicio.query.get(id_servicio)
    if not s:
        return error_response("Servicio no encontrado", 404)
    return jsonify({
        "id_servicio": s.id_servicio,
        "nombre": s.nombre,
        "descripcion": s.descripcion,
        "precio_aprox": s.precio_aprox,
        "imagen": s.imagen
    }), 200

@api_bp.route('/servicios', methods=['POST'])
def create_servicio():
    data = request.get_json() or {}
    nombre = (data.get('nombre') or '').strip()
    descripcion = (data.get('descripcion') or '').strip()
    precio_aprox = data.get('precio_aprox')
    imagen = (data.get('imagen') or '').strip()

    if not nombre:
        return error_response("El nombre es requerido")

    try:
        nuevo = Servicio(
            nombre=nombre,
            descripcion=descripcion,
            precio_aprox=float(precio_aprox) if precio_aprox else None,
            imagen=imagen
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_servicio": nuevo.id_servicio,
            "nombre": nuevo.nombre,
            "precio_aprox": nuevo.precio_aprox
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/servicios/<int:id_servicio>', methods=['PUT'])
def update_servicio(id_servicio):
    s = Servicio.query.get(id_servicio)
    if not s:
        return error_response("Servicio no encontrado", 404)

    data = request.get_json() or {}
    if 'nombre' in data: s.nombre = (data['nombre'] or '').strip()
    if 'descripcion' in data: s.descripcion = (data['descripcion'] or '').strip()
    if 'precio_aprox' in data: s.precio_aprox = float(data['precio_aprox']) if data['precio_aprox'] is not None and data['precio_aprox'] != '' else None
    if 'imagen' in data: s.imagen = (data['imagen'] or '').strip()

    try:
        db.session.commit()
        return jsonify({
            "id_servicio": s.id_servicio,
            "nombre": s.nombre,
            "precio_aprox": s.precio_aprox
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/servicios/<int:id_servicio>', methods=['DELETE'])
def delete_servicio(id_servicio):
    s = Servicio.query.get(id_servicio)
    if not s:
        return error_response("Servicio no encontrado", 404)
    try:
        db.session.delete(s)
        db.session.commit()
        return jsonify({"message": "Servicio eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


# =========================================================================
# 4. CITAS CRUD
# =========================================================================
@api_bp.route('/citas', methods=['GET'])
def get_citas():
    try:
        citas = Cita.query.all()
        res = []
        for c in citas:
            u = Usuario.query.get(c.id_usuario)
            ch = Coche.query.get(c.id_coche)
            tc = TipoCita.query.get(c.id_tipo_cita) if c.id_tipo_cita else None
            res.append({
                "id_cita": c.id_cita,
                "id_usuario": c.id_usuario,
                "nombre_usuario": f"{u.nombre} {u.apellido}" if u else "Desconocido",
                "id_coche": c.id_coche,
                "vehiculo": f"{ch.marca} {ch.modelo} ({ch.placa})" if ch else "Desconocido",
                "id_tipo_cita": c.id_tipo_cita,
                "nombre_tipo_cita": tc.nombre if tc else "Sin definir",
                "fecha": c.fecha.isoformat() if c.fecha else None,
                "hora": c.hora.strftime('%H:%M:%S') if c.hora else None,
                "motivo_cita": c.motivo_cita,
                "estado": c.estado,
                "enlace_whatsapp": c.enlace_whatsapp
            })
        return jsonify(res), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error GET /citas: {e}")
        return error_response(f"Error al consultar citas: {str(e)}", 500)

@api_bp.route('/citas/<int:id_cita>', methods=['GET'])
def get_cita(id_cita):
    c = Cita.query.get(id_cita)
    if not c:
        return error_response("Cita no encontrada", 404)
    u = Usuario.query.get(c.id_usuario)
    ch = Coche.query.get(c.id_coche)
    tc = TipoCita.query.get(c.id_tipo_cita) if c.id_tipo_cita else None
    return jsonify({
        "id_cita": c.id_cita,
        "id_usuario": c.id_usuario,
        "nombre_usuario": f"{u.nombre} {u.apellido}" if u else "Desconocido",
        "id_coche": c.id_coche,
        "vehiculo": f"{ch.marca} {ch.modelo} ({ch.placa})" if ch else "Desconocido",
        "id_tipo_cita": c.id_tipo_cita,
        "nombre_tipo_cita": tc.nombre if tc else "Sin definir",
        "fecha": c.fecha.isoformat() if c.fecha else None,
        "hora": c.hora.strftime('%H:%M:%S') if c.hora else None,
        "motivo_cita": c.motivo_cita,
        "estado": c.estado,
        "enlace_whatsapp": c.enlace_whatsapp
    }), 200

@api_bp.route('/citas', methods=['POST'])
def create_cita():
    data = request.get_json() or {}
    id_usuario = data.get('id_usuario')
    id_coche = data.get('id_coche')
    id_tipo_cita = data.get('id_tipo_cita')
    fecha_str = data.get('fecha')
    hora_str = data.get('hora')
    motivo = (data.get('motivo_cita') or '').strip()
    estado = (data.get('estado') or 'pendiente').strip()
    whatsapp = (data.get('enlace_whatsapp') or '').strip()

    # Cast foreign keys safely
    id_usuario = int(id_usuario) if id_usuario else None
    id_coche = int(id_coche) if id_coche else None
    id_tipo_cita = int(id_tipo_cita) if id_tipo_cita else None

    if not id_usuario or not id_coche or not fecha_str or not hora_str:
        return error_response("Campos requeridos: id_usuario, id_coche, fecha (YYYY-MM-DD), hora (HH:MM)")

    if not Usuario.query.get(id_usuario):
        return error_response("El usuario asociado no existe")
    if not Coche.query.get(id_coche):
        return error_response("El coche asociado no existe")

    fecha = parse_date(fecha_str)
    hora = parse_time(hora_str)
    if not fecha or not hora:
        return error_response("Formato de fecha o hora incorrecto")

    try:
        nuevo = Cita(
            id_usuario=id_usuario,
            id_coche=id_coche,
            id_tipo_cita=id_tipo_cita,
            fecha=fecha,
            hora=hora,
            motivo_cita=motivo,
            estado=estado,
            enlace_whatsapp=whatsapp
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_cita": nuevo.id_cita,
            "id_usuario": nuevo.id_usuario,
            "fecha": nuevo.fecha.isoformat(),
            "estado": nuevo.estado
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/citas/<int:id_cita>', methods=['PUT'])
def update_cita(id_cita):
    c = Cita.query.get(id_cita)
    if not c:
        return error_response("Cita no encontrada", 404)

    data = request.get_json() or {}
    if 'id_usuario' in data:
        val_usuario = int(data['id_usuario']) if data['id_usuario'] else None
        if not val_usuario or not Usuario.query.get(val_usuario):
            return error_response("El usuario asociado no existe")
        c.id_usuario = val_usuario
    if 'id_coche' in data:
        val_coche = int(data['id_coche']) if data['id_coche'] else None
        if not val_coche or not Coche.query.get(val_coche):
            return error_response("El coche asociado no existe")
        c.id_coche = val_coche
    if 'id_tipo_cita' in data:
        c.id_tipo_cita = int(data['id_tipo_cita']) if data['id_tipo_cita'] else None
    if 'fecha' in data:
        fecha = parse_date(data['fecha'])
        if not fecha:
            return error_response("Formato de fecha incorrecto")
        c.fecha = fecha
    if 'hora' in data:
        hora = parse_time(data['hora'])
        if not hora:
            return error_response("Formato de hora incorrecto")
        c.hora = hora
    if 'motivo_cita' in data: c.motivo_cita = (data['motivo_cita'] or '').strip()
    if 'estado' in data: c.estado = (data['estado'] or 'pendiente').strip()
    if 'enlace_whatsapp' in data: c.enlace_whatsapp = (data['enlace_whatsapp'] or '').strip()

    try:
        db.session.commit()
        return jsonify({
            "id_cita": c.id_cita,
            "estado": c.estado,
            "fecha": c.fecha.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/citas/<int:id_cita>', methods=['DELETE'])
def delete_cita(id_cita):
    c = Cita.query.get(id_cita)
    if not c:
        return error_response("Cita no encontrada", 404)
    try:
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Cita eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


# =========================================================================
# 5. HISTORIAL MANTENIMIENTO CRUD
# =========================================================================
@api_bp.route('/historial', methods=['GET'])
def get_historial():
    historial = HistorialMantenimiento.query.all()
    res = []
    for hm in historial:
        c = Coche.query.get(hm.id_coche)
        admin = Usuario.query.get(hm.id_admin) if hm.id_admin else None
        ds = DetalleServicio.query.get(hm.id_detalle_servicio) if hm.id_detalle_servicio else None
        serv = Servicio.query.get(ds.id_servicio) if (ds and ds.id_servicio) else None
        res.append({
            "id_historial": hm.id_historial,
            "id_coche": hm.id_coche,
            "vehiculo": f"{c.marca} {c.modelo} ({c.placa})" if c else "Desconocido",
            "id_detalle_servicio": hm.id_detalle_servicio,
            "servicio": serv.nombre if serv else "General / Diagnóstico",
            "id_admin": hm.id_admin,
            "admin_nombre": f"{admin.nombre} {admin.apellido}" if admin else "Taller",
            "fecha_mantenimiento": hm.fecha_mantenimiento.isoformat() if hm.fecha_mantenimiento else None,
            "kilometraje": hm.kilometraje,
            "costo": hm.costo,
            "observaciones": hm.observaciones
        })
    return jsonify(res), 200

@api_bp.route('/historial/<int:id_historial>', methods=['GET'])
def get_historial_item(id_historial):
    hm = HistorialMantenimiento.query.get(id_historial)
    if not hm:
        return error_response("Historial no encontrado", 404)
    c = Coche.query.get(hm.id_coche)
    admin = Usuario.query.get(hm.id_admin) if hm.id_admin else None
    ds = DetalleServicio.query.get(hm.id_detalle_servicio) if hm.id_detalle_servicio else None
    serv = Servicio.query.get(ds.id_servicio) if (ds and ds.id_servicio) else None
    return jsonify({
        "id_historial": hm.id_historial,
        "id_coche": hm.id_coche,
        "vehiculo": f"{c.marca} {c.modelo} ({c.placa})" if c else "Desconocido",
        "id_detalle_servicio": hm.id_detalle_servicio,
        "servicio": serv.nombre if serv else "General / Diagnóstico",
        "id_admin": hm.id_admin,
        "admin_nombre": f"{admin.nombre} {admin.apellido}" if admin else "Taller",
        "fecha_mantenimiento": hm.fecha_mantenimiento.isoformat() if hm.fecha_mantenimiento else None,
        "kilometraje": hm.kilometraje,
        "costo": hm.costo,
        "observaciones": hm.observaciones
    }), 200

@api_bp.route('/historial', methods=['POST'])
def create_historial():
    data = request.get_json() or {}
    id_coche = data.get('id_coche')
    id_detalle_servicio = data.get('id_detalle_servicio')  # Can be null
    id_admin = data.get('id_admin')                      # Can be null
    fecha_str = data.get('fecha_mantenimiento')
    kilometraje = data.get('kilometraje')
    costo = data.get('costo')
    observaciones = (data.get('observaciones') or '').strip()

    # Safely cast keys and numbers
    id_coche = int(id_coche) if id_coche else None
    id_detalle_servicio = int(id_detalle_servicio) if id_detalle_servicio else None
    id_admin = int(id_admin) if id_admin else None

    if not id_coche or not fecha_str or kilometraje is None or costo is None or kilometraje == '' or costo == '':
        return error_response("Campos requeridos: id_coche, fecha_mantenimiento (YYYY-MM-DD), kilometraje, costo")

    if not Coche.query.get(id_coche):
        return error_response("El coche asociado no existe")
    if id_admin and not Usuario.query.get(id_admin):
        return error_response("El administrador asociado no existe")

    fecha = parse_date(fecha_str)
    if not fecha:
        return error_response("Formato de fecha incorrecto")

    try:
        nuevo = HistorialMantenimiento(
            id_coche=id_coche,
            id_detalle_servicio=id_detalle_servicio,
            id_admin=id_admin,
            fecha_mantenimiento=fecha,
            kilometraje=int(kilometraje),
            costo=float(costo),
            observaciones=observaciones
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({
            "id_historial": nuevo.id_historial,
            "id_coche": nuevo.id_coche,
            "costo": nuevo.costo,
            "fecha_mantenimiento": nuevo.fecha_mantenimiento.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/historial/<int:id_historial>', methods=['PUT'])
def update_historial(id_historial):
    hm = HistorialMantenimiento.query.get(id_historial)
    if not hm:
        return error_response("Historial no encontrado", 404)

    data = request.get_json() or {}
    if 'id_coche' in data:
        val_coche = int(data['id_coche']) if data['id_coche'] else None
        if not val_coche or not Coche.query.get(val_coche):
            return error_response("El coche asociado no existe")
        hm.id_coche = val_coche
    if 'id_detalle_servicio' in data:
        hm.id_detalle_servicio = int(data['id_detalle_servicio']) if data['id_detalle_servicio'] else None
    if 'id_admin' in data:
        val_admin = int(data['id_admin']) if data['id_admin'] else None
        if val_admin and not Usuario.query.get(val_admin):
            return error_response("El administrador asociado no existe")
        hm.id_admin = val_admin
    if 'fecha_mantenimiento' in data:
        fecha = parse_date(data['fecha_mantenimiento'])
        if not fecha:
            return error_response("Formato de fecha incorrecto")
        hm.fecha_mantenimiento = fecha
    if 'kilometraje' in data:
        hm.kilometraje = int(data['kilometraje']) if data['kilometraje'] is not None and data['kilometraje'] != '' else None
    if 'costo' in data:
        hm.costo = float(data['costo']) if data['costo'] is not None and data['costo'] != '' else None
    if 'observaciones' in data: hm.observaciones = (data['observaciones'] or '').strip()

    try:
        db.session.commit()
        return jsonify({
            "id_historial": hm.id_historial,
            "costo": hm.costo,
            "fecha_mantenimiento": hm.fecha_mantenimiento.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)

@api_bp.route('/historial/<int:id_historial>', methods=['DELETE'])
def delete_historial(id_historial):
    hm = HistorialMantenimiento.query.get(id_historial)
    if not hm:
        return error_response("Historial no encontrado", 404)
    try:
        db.session.delete(hm)
        db.session.commit()
        return jsonify({"message": "Historial eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error: {str(e)}", 500)


# =========================================================================
# 6. AUXILIAR: MOCK/PUBLIC NORTHWIND API INTEGRATION SIMULATOR
# =========================================================================
# This provides a Northwind compatibility layer to demonstrate integrating Northwind data
@api_bp.route('/northwind/products', methods=['GET'])
def get_northwind_products():
    # Simulates Northwind products, e.g., transmission parts
    products = [
        {"id": 1, "name": "Filtro de Transmisión Automática A340E", "category": "Filtros", "price": 450.00, "stock": 15, "supplier": "Toyota Parts MX"},
        {"id": 2, "name": "Aceite de Transmisión ATF Dexron VI 1L", "category": "Fluidos", "price": 180.00, "stock": 50, "supplier": "Mobil Premium"},
        {"id": 3, "name": "Kit de Embragues (Clutches) GM 4L60E", "category": "Reparación Interna", "price": 1250.00, "stock": 8, "supplier": "Transtec"},
        {"id": 4, "name": "Solenoide de Presión (EPC) Ford 4R70W", "category": "Eléctrico", "price": 850.00, "stock": 12, "supplier": "BorgWarner"},
        {"id": 5, "name": "Convertidor de Par (Turbina) 10-Inch", "category": "Convertidores", "price": 3200.00, "stock": 3, "supplier": "Dacco"},
        {"id": 6, "name": "Empaque de Cárter de Transmisión", "category": "Sellos y Juntas", "price": 95.00, "stock": 25, "supplier": "Fel-Pro"},
        {"id": 7, "name": "Cuerpo de Válvulas Reconstruido AW55-50SN", "category": "Control Hidráulico", "price": 4800.00, "stock": 2, "supplier": "Sonnax"}
    ]
    return jsonify(products), 200
