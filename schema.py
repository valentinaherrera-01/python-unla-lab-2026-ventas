from pydantic import BaseModel, ConfigDict


class ProductoCreate(BaseModel):
    nombre: str
    precio: float

    model_config = ConfigDict(from_attributes=True)


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float

    model_config = ConfigDict(from_attributes=True)
