from datetime import date, time

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator


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
    id_producto: int | None = None
    cantidad: int | None = None
    id_carrito: int | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value

    @model_validator(mode="after")
    def validar_modo_venta(self):
        modo_producto = self.id_producto is not None
        modo_carrito = self.id_carrito is not None

        if modo_producto == modo_carrito:
            raise ValueError("Debe indicar id_producto y cantidad, o id_carrito (sólo uno de los dos)")
        if modo_producto and self.cantidad is None:
            raise ValueError("La cantidad es obligatoria al indicar id_producto")
        return self


class VentaUpdate(BaseModel):
    fecha: date | None = None
    hora: time | None = None
    id_producto: int | None = None
    cantidad: int | None = None
    id_carrito: int | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value

    @model_validator(mode="after")
    def validar_modo_venta(self):
        modo_producto = self.id_producto is not None
        modo_carrito = self.id_carrito is not None

        if modo_producto and modo_carrito:
            raise ValueError("No puede indicar id_producto e id_carrito a la vez")
        if modo_producto and self.cantidad is None:
            raise ValueError("La cantidad es obligatoria al indicar id_producto")
        if modo_carrito and self.cantidad is not None:
            raise ValueError("No puede mezclar la venta directa con la venta por carrito")
        return self


class CarritoVentaCreate(BaseModel):
    id_carrito: int

    model_config = ConfigDict(from_attributes=True)


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


class VentaResponse(BaseModel):
    id: int
    fecha: date
    hora: time
    producto: ProductoResponse | None = None
    cantidad: int | None = None
    carrito: CarritoResponse | None = None
    precio_total: float

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("hora")
    @classmethod
    def serializar_hora(cls, value: time) -> str:
        return value.strftime("%H:%M")
