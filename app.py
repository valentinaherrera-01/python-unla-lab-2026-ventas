from fastapi import FastAPI, HTTPException, status

from database import Producto, db_session
from schema import ProductoCreate, ProductoResponse

app = FastAPI(
    title="API Ventas 2026",
    description="API REST para gestionar ventas de productos - Seminario de Lenguajes Python (UNLa)",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "API Ventas 2026 - Laboratorio Seminario de Lenguajes Python"}


@app.post("/productos", status_code=status.HTTP_201_CREATED, response_model=ProductoResponse)
async def crear_producto(producto_data: ProductoCreate):
    try:
        producto_existente = Producto.query.filter_by(nombre=producto_data.nombre).first()

        if producto_existente:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El producto ya existe")

        producto = Producto(
            nombre=producto_data.nombre,
            precio=producto_data.precio,
        )

        db_session.add(producto)
        db_session.commit()
        db_session.refresh(producto)

        return producto
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar crear el producto: {e}",
        )


@app.get("/productos", status_code=status.HTTP_200_OK, response_model=list[ProductoResponse])
async def listar_productos():
    try:
        productos = Producto.query.all()
        return productos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener los productos: {e}",
        )


@app.get("/productos/{producto_id}", status_code=status.HTTP_200_OK, response_model=ProductoResponse)
async def obtener_producto(producto_id: int):
    try:
        producto = db_session.get(Producto, producto_id)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        return producto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener el producto con id {producto_id}: {e}",
        )


@app.put("/productos/{producto_id}", status_code=status.HTTP_200_OK, response_model=ProductoResponse)
async def actualizar_producto(producto_id: int, producto_data: ProductoCreate):
    try:
        producto = db_session.get(Producto, producto_id)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        producto.nombre = producto_data.nombre
        producto.precio = producto_data.precio

        db_session.commit()
        db_session.refresh(producto)

        return producto
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar actualizar el producto con id {producto_id}: {e}",
        )


@app.delete("/productos/{producto_id}", status_code=status.HTTP_200_OK)
async def eliminar_producto(producto_id: int):
    try:
        producto = db_session.get(Producto, producto_id)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        db_session.delete(producto)
        db_session.commit()

        return {"message": f"Producto con id {producto_id} eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar eliminar el producto con id {producto_id}: {e}",
        )
