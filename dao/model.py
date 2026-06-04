from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Date, Time, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime

db = SQLAlchemy()

# --- TABLAS ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    correo = Column(String(100), unique=True)
    contrasena = Column(String(255))
    telefono = Column(String(20))
    rol = Column(String(50))
    foto = Column(String(255))   # ← agregado

    coches = relationship("Coche", back_populates="usuario")
    citas = relationship("Cita", back_populates="usuario")


class Coche(db.Model):
    __tablename__ = 'coches'
    id_coche = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'))
    marca = Column(String(50))
    modelo = Column(String(50))
    anio = Column(Integer)
    placa = Column(String(20))
    foto = Column(String(255))   # ← agregado

    usuario = relationship("Usuario", back_populates="coches")
    citas = relationship("Cita", back_populates="coche")
    detalle_servicios = relationship("DetalleServicio", back_populates="coche")
    mantenimientos = relationship("HistorialMantenimiento", back_populates="coche")


class Servicio(db.Model):
    __tablename__ = 'servicios'
    id_servicio = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(Text)
    precio_aprox = Column(Float)
    imagen = Column(String(255))  # ← coincide con tu DB

    detalle_servicios = relationship("DetalleServicio", back_populates="servicio")


class TipoCita(db.Model):
    __tablename__ = 'tipos_cita'
    id_tipo_cita = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(Text)

    citas = relationship("Cita", back_populates="tipo_cita")


class Cita(db.Model):
    __tablename__ = 'citas'
    id_cita = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'))
    id_coche = Column(Integer, ForeignKey('coches.id_coche'))
    id_tipo_cita = Column(Integer, ForeignKey('tipos_cita.id_tipo_cita'), nullable=True)
    fecha = Column(Date)
    hora = Column(Time)
    motivo_cita = Column(String(255))
    estado = Column(String(50))  # ← mysql ENUM manejado como string
    enlace_whatsapp = Column(String(255))

    usuario = relationship("Usuario", back_populates="citas")
    coche = relationship("Coche", back_populates="citas")
    tipo_cita = relationship("TipoCita", back_populates="citas")
    detalle_servicios = relationship("DetalleServicio", back_populates="cita")
    horarios = relationship("HorarioDisponible", back_populates="cita")


class HorarioDisponible(db.Model):
    __tablename__ = 'horarios_disponibles'
    id_horario = Column(Integer, primary_key=True)
    fecha = Column(Date)
    hora = Column(Time)
    disponible = Column(Boolean)
    id_cita = Column(Integer, ForeignKey('citas.id_cita'))

    cita = relationship("Cita", back_populates="horarios")


class DetalleServicio(db.Model):
    __tablename__ = 'detalle_servicio'
    id_detalle = Column(Integer, primary_key=True)
    id_coche = Column(Integer, ForeignKey('coches.id_coche'))
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'))
    id_cita = Column(Integer, ForeignKey('citas.id_cita'), nullable=True)
    fecha = Column(Date)
    estado = Column(String(50))
    observaciones = Column(Text)
    anadidos = Column(Text)
    costo_extra = Column(Float)

    coche = relationship("Coche", back_populates="detalle_servicios")
    servicio = relationship("Servicio", back_populates="detalle_servicios")
    cita = relationship("Cita", back_populates="detalle_servicios")
    mantenimientos = relationship("HistorialMantenimiento", back_populates="detalle_servicio")


class HistorialMantenimiento(db.Model):
    __tablename__ = 'historial_mantenimientos'
    id_historial = Column(Integer, primary_key=True)
    id_coche = Column(Integer, ForeignKey('coches.id_coche'))
    id_detalle_servicio = Column(Integer, ForeignKey('detalle_servicio.id_detalle'))
    id_admin = Column(Integer, ForeignKey('usuarios.id_usuario'))
    fecha_mantenimiento = Column(Date)
    kilometraje = Column(Integer)
    costo = Column(Float)
    observaciones = Column(Text)

    coche = relationship("Coche", back_populates="mantenimientos")
    detalle_servicio = relationship("DetalleServicio", back_populates="mantenimientos")
    admin = relationship("Usuario")


def inicializar_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print("Base de datos inicializada.")
