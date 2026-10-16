from datetime import date, time

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator


class ProductoCreate(BaseModel):
    nombre: str
    precio: float

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre del producto no puede estar vacío")
        return value

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, value: float) -> float:
        if value < 0:
            raise ValueError("El precio del producto no puede ser negativo")
        return value


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float

    model_config = ConfigDict(from_attributes=True)


class VentaCreate(BaseModel):
    fecha: date
    hora: time
    id_producto: int
    cantidad: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value


class VentaResponse(BaseModel):
    id: int
    fecha: date
    hora: time
    producto: ProductoResponse
    cantidad: int
    precio_total: float

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("hora")
    @classmethod
    def serializar_hora(cls, value: time) -> str:
        return value.strftime("%H:%M")


class CarritoCreate(BaseModel):
    fecha_creacion: date
    estado: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ("abierto", "cerrado"):
            raise ValueError("El estado del carrito debe ser 'abierto' o 'cerrado'")
        return value


class CarritoUpdate(BaseModel):
    fecha_creacion: date | None = None
    estado: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().lower()
        if value not in ("abierto", "cerrado"):
            raise ValueError("El estado del carrito debe ser 'abierto' o 'cerrado'")
        return value


class CarritoProductoCreate(BaseModel):
    id_producto: int
    cantidad: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value


class CarritoProductoResponse(BaseModel):
    id: int
    producto: ProductoResponse
    cantidad: int

    model_config = ConfigDict(from_attributes=True)


class CarritoResponse(BaseModel):
    id: int
    fecha_creacion: date
    estado: str
    productos: list[CarritoProductoResponse]

    model_config = ConfigDict(from_attributes=True)
