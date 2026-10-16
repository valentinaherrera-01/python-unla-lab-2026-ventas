from datetime import date, time

from pydantic import BaseModel, ConfigDict, field_validator


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
