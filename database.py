from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Time, create_engine
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker

engine = create_engine("sqlite:///database.db")
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)


class Carrito(Base):
    __tablename__ = "carritos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    productos = relationship("CarritoProducto", back_populates="carrito", cascade="all, delete-orphan")
    venta = relationship("Venta", back_populates="carrito", uselist=False)


class CarritoProducto(Base):
    __tablename__ = "carrito_producto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_carrito = Column(Integer, ForeignKey("carritos.id"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)

    carrito = relationship("Carrito", back_populates="productos")
    producto = relationship("Producto")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=True)
    cantidad = Column(Integer, nullable=True)
    id_carrito = Column(Integer, ForeignKey("carritos.id"), unique=True, nullable=True)
    precio_total = Column(Float, nullable=False)

    producto = relationship("Producto")
    carrito = relationship("Carrito", back_populates="venta", uselist=False)


Base.metadata.create_all(engine)
