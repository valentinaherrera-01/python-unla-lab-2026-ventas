from fastapi import FastAPI, HTTPException, status

from database import Carrito, CarritoProducto, Producto, Venta, db_session
from schema import (
    CarritoCreate,
    CarritoProductoCreate,
    CarritoProductoResponse,
    CarritoResponse,
    CarritoUpdate,
    CarritoVentaCreate,
    ProductoCreate,
    ProductoResponse,
    VentaCreate,
    VentaResponse,
    VentaUpdate,
)

app = FastAPI(
    title="API Ventas 2026",
    description="API REST para gestionar ventas de productos - Seminario de Lenguajes Python (UNLa)",
    version="1.0.0",
)


def calcular_precio_total(venta: Venta) -> float:
    if venta.id_carrito is not None:
        carrito = db_session.get(Carrito, venta.id_carrito)
        return round(sum(item.producto.precio * item.cantidad for item in carrito.productos), 2)

    producto = db_session.get(Producto, venta.id_producto)
    return round(producto.precio * venta.cantidad, 2)


def carrito_asignado_a_otra_venta(id_carrito: int, venta_id: int | None = None) -> Venta | None:
    consulta = Venta.query.filter_by(id_carrito=id_carrito)
    if venta_id is not None:
        consulta = consulta.filter(Venta.id != venta_id)
    return consulta.first()


def validar_carrito_para_vender(carrito_id: int, venta_id: int | None = None) -> Carrito:
    carrito = db_session.get(Carrito, carrito_id)

    if not carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

    if carrito_asignado_a_otra_venta(carrito_id, venta_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El carrito ya se encuentra asociado a otra venta",
        )

    if carrito.estado != "cerrado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede asociar a una venta un carrito en estado 'cerrado'",
        )

    return carrito


def validar_carrito_modificable(carrito_id: int) -> Carrito:
    carrito = db_session.get(Carrito, carrito_id)

    if not carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

    if carrito.venta is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un carrito asociado a una venta no puede ser modificado ni eliminado",
        )

    return carrito


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

        registrado_en_carrito = CarritoProducto.query.filter_by(id_producto=producto_id).first()

        if registrado_en_carrito:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar un producto que este registrado en algun carrito",
            )

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


@app.post("/ventas", status_code=status.HTTP_201_CREATED, response_model=VentaResponse, response_model_exclude_none=True)
async def crear_venta(venta_data: VentaCreate):
    try:
        venta = Venta(
            fecha=venta_data.fecha,
            hora=venta_data.hora,
        )

        if venta_data.id_carrito is not None:
            validar_carrito_para_vender(venta_data.id_carrito)
            venta.id_carrito = venta_data.id_carrito
        else:
            producto = db_session.get(Producto, venta_data.id_producto)

            if not producto:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

            venta.id_producto = venta_data.id_producto
            venta.cantidad = venta_data.cantidad

        venta.precio_total = calcular_precio_total(venta)

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


@app.get("/ventas", status_code=status.HTTP_200_OK, response_model=list[VentaResponse], response_model_exclude_none=True)
async def listar_ventas():
    try:
        ventas = Venta.query.all()
        return ventas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener las ventas: {e}",
        )


@app.get("/ventas/{venta_id}", status_code=status.HTTP_200_OK, response_model=VentaResponse, response_model_exclude_none=True)
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


@app.put("/ventas/{venta_id}", status_code=status.HTTP_200_OK, response_model=VentaResponse, response_model_exclude_none=True)
async def actualizar_venta(venta_id: int, venta_data: VentaUpdate):
    try:
        venta = db_session.get(Venta, venta_id)

        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        if venta_data.fecha is not None:
            venta.fecha = venta_data.fecha
        if venta_data.hora is not None:
            venta.hora = venta_data.hora

        if venta_data.id_carrito is not None:
            validar_carrito_para_vender(venta_data.id_carrito, venta_id)
            venta.id_carrito = venta_data.id_carrito
            venta.id_producto = None
            venta.cantidad = None
        elif venta_data.id_producto is not None:
            producto = db_session.get(Producto, venta_data.id_producto)

            if not producto:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

            venta.id_producto = venta_data.id_producto
            venta.cantidad = venta_data.cantidad
            venta.id_carrito = None

        venta.precio_total = calcular_precio_total(venta)

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


@app.post("/ventas/{venta_id}/carrito", status_code=status.HTTP_200_OK, response_model=VentaResponse, response_model_exclude_none=True)
async def asignar_carrito_a_venta(venta_id: int, carrito_data: CarritoVentaCreate):
    try:
        venta = db_session.get(Venta, venta_id)

        if not venta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        validar_carrito_para_vender(carrito_data.id_carrito, venta_id)

        venta.id_carrito = carrito_data.id_carrito
        venta.id_producto = None
        venta.cantidad = None
        venta.precio_total = calcular_precio_total(venta)

        db_session.commit()
        db_session.refresh(venta)

        return venta
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar asignar el carrito a la venta con id {venta_id}: {e}",
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


@app.post("/carritos", status_code=status.HTTP_201_CREATED, response_model=CarritoResponse)
async def crear_carrito(carrito_data: CarritoCreate):
    try:
        carrito = Carrito(
            fecha_creacion=carrito_data.fecha_creacion,
            estado=carrito_data.estado,
        )

        db_session.add(carrito)
        db_session.commit()
        db_session.refresh(carrito)

        return carrito
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar crear el carrito: {e}",
        )


@app.get("/carritos", status_code=status.HTTP_200_OK, response_model=list[CarritoResponse])
async def listar_carritos():
    try:
        carritos = Carrito.query.all()
        return carritos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener los carritos: {e}",
        )


@app.get("/carritos/{carrito_id}", status_code=status.HTTP_200_OK, response_model=CarritoResponse)
async def obtener_carrito(carrito_id: int):
    try:
        carrito = db_session.get(Carrito, carrito_id)

        if not carrito:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        return carrito
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar obtener el carrito con id {carrito_id}: {e}",
        )


@app.put("/carritos/{carrito_id}", status_code=status.HTTP_200_OK, response_model=CarritoResponse)
async def actualizar_carrito(carrito_id: int, carrito_data: CarritoUpdate):
    try:
        carrito = validar_carrito_modificable(carrito_id)

        if carrito_data.fecha_creacion is not None:
            carrito.fecha_creacion = carrito_data.fecha_creacion
        if carrito_data.estado is not None:
            carrito.estado = carrito_data.estado

        db_session.commit()
        db_session.refresh(carrito)

        return carrito
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar actualizar el carrito con id {carrito_id}: {e}",
        )


@app.delete("/carritos/{carrito_id}", status_code=status.HTTP_200_OK)
async def eliminar_carrito(carrito_id: int):
    try:
        carrito = validar_carrito_modificable(carrito_id)

        db_session.delete(carrito)
        db_session.commit()

        return {"message": f"Carrito con id {carrito_id} eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar eliminar el carrito con id {carrito_id}: {e}",
        )


@app.post("/carritos/{carrito_id}/productos", status_code=status.HTTP_201_CREATED, response_model=CarritoProductoResponse)
async def agregar_producto_al_carrito(carrito_id: int, producto_data: CarritoProductoCreate):
    try:
        carrito = db_session.get(Carrito, carrito_id)

        if not carrito:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        if carrito.venta is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un carrito asociado a una venta no puede ser modificado",
            )

        if carrito.estado != "abierto":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden agregar productos a un carrito abierto",
            )

        producto = db_session.get(Producto, producto_data.id_producto)

        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

        carrito_producto = CarritoProducto.query.filter_by(
            id_carrito=carrito_id, id_producto=producto_data.id_producto
        ).first()

        if carrito_producto:
            carrito_producto.cantidad += producto_data.cantidad
        else:
            carrito_producto = CarritoProducto(
                id_carrito=carrito_id,
                id_producto=producto_data.id_producto,
                cantidad=producto_data.cantidad,
            )
            db_session.add(carrito_producto)

        db_session.commit()
        db_session.refresh(carrito_producto)

        return carrito_producto
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar agregar el producto al carrito: {e}",
        )


@app.delete("/carritos/{carrito_id}/productos/{producto_id}", status_code=status.HTTP_200_OK)
async def quitar_producto_del_carrito(carrito_id: int, producto_id: int):
    try:
        carrito = db_session.get(Carrito, carrito_id)

        if not carrito:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        if carrito.venta is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un carrito asociado a una venta no puede ser modificado",
            )

        if carrito.estado != "abierto":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden quitar productos de un carrito abierto",
            )

        carrito_producto = CarritoProducto.query.filter_by(
            id_carrito=carrito_id, id_producto=producto_id
        ).first()

        if not carrito_producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto no se encuentra en el carrito",
            )

        db_session.delete(carrito_producto)
        db_session.commit()

        return {"message": f"Producto con id {producto_id} quitado del carrito con id {carrito_id}"}
    except HTTPException:
        raise
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al intentar quitar el producto del carrito: {e}",
        )
