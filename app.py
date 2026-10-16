from fastapi import FastAPI, HTTPException, status

from database import Producto, Venta, db_session
from schema import ProductoCreate, ProductoResponse, VentaCreate, VentaResponse

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


@app.post("/ventas", status_code=status.HTTP_201_CREATED, response_model=VentaResponse)
async def crear_venta(venta_data: VentaCreate):
    try:
        producto = db_session.get(Producto, venta_data.id_producto)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

        venta = Venta(
            fecha=venta_data.fecha,
            hora=venta_data.hora,
            id_producto=venta_data.id_producto,
            cantidad=venta_data.cantidad,
            precio_total=(producto.precio * venta_data.cantidad),
        )

        db_session.add(venta)
        db_session.commit()
        db_session.refresh(venta)

        return venta
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar crear la venta: {e}",
        )


@app.get("/ventas", status_code=status.HTTP_200_OK, response_model=list[VentaResponse])
async def listar_ventas():
    try:
        ventas = Venta.query.all()
        return ventas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener las ventas: {e}",
        )


@app.get("/ventas/{venta_id}", status_code=status.HTTP_200_OK, response_model=VentaResponse)
async def obtener_venta(venta_id: int):
    try:
        venta = db_session.get(Venta, venta_id)

        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        return venta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener la venta con id {venta_id}: {e}",
        )


@app.put("/ventas/{venta_id}", status_code=status.HTTP_200_OK, response_model=VentaResponse)
async def actualizar_venta(venta_id: int, venta_data: VentaCreate):
    try:
        venta = db_session.get(Venta, venta_id)

        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        producto = db_session.get(Producto, venta_data.id_producto)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

        venta.fecha = venta_data.fecha
        venta.hora = venta_data.hora
        venta.id_producto = venta_data.id_producto
        venta.cantidad = venta_data.cantidad
        venta.precio_total = (producto.precio * venta_data.cantidad)

        db_session.commit()
        db_session.refresh(venta)

        return venta
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar actualizar la venta con id {venta_id}: {e}",
        )


@app.delete("/ventas/{venta_id}", status_code=status.HTTP_200_OK)
async def eliminar_venta(venta_id: int):
    try:
        venta = db_session.get(Venta, venta_id)

        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        db_session.delete(venta)
        db_session.commit()

        return {"message": f"Venta con id {venta_id} eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar eliminar la venta con id {venta_id}: {e}",
        )
