import os
import sys

import httpx

BASE = os.environ.get("API_BASE", "http://localhost:8000")
pasados = 0
fallidos = 0


def check(desc, cond, extra=""):
    global pasados, fallidos
    if cond:
        pasados += 1
        print(f"  PASS: {desc}")
    else:
        fallidos += 1
        print(f"  FAIL: {desc} | {extra}")


def req(m, url, body=None):
    try:
        return httpx.request(m, f"{BASE}{url}", json=body, timeout=10)
    except Exception as e:
        class R:
            status_code = 0
            text = f"conexion fallida: {e}"
            def json(self):
                return {}
        return R()


print("=== VERSION BASE: ABM Productos ===")
r = req("POST", "/productos", {"nombre": "Esponja", "precio": 11.11})
check("POST producto Esponja 201", r.status_code == 201 and r.json() == {"id": 1, "nombre": "Esponja", "precio": 11.11}, r.text)
r = req("POST", "/productos", {"nombre": "Arroz", "precio": 300})
check("POST producto Arroz 201", r.status_code == 201, r.text)
r = req("POST", "/productos", {"nombre": "Arroz", "precio": 300})
check("POST producto duplicado 409", r.status_code == 409, r.text)
r = req("GET", "/productos")
check("GET productos lista de 2", r.status_code == 200 and len(r.json()) == 2, r.text)
r = req("GET", "/productos/1")
check("GET producto/1", r.status_code == 200 and r.json()["nombre"] == "Esponja", r.text)
r = req("GET", "/productos/99")
check("GET producto/99 404", r.status_code == 404, r.text)
r = req("PUT", "/productos/1", {"nombre": "Esponja Rapida", "precio": 12.5})
check("PUT producto/1", r.status_code == 200 and r.json()["precio"] == 12.5, r.text)
r = req("PUT", "/productos/1", {"nombre": "  ", "precio": 1})
check("PUT nombre vacio 422", r.status_code == 422, r.text)
r = req("POST", "/productos", {"nombre": "Yerba", "precio": -3})
check("POST precio negativo 422", r.status_code == 422, r.text)

print("=== VERSION BASE: ABM Ventas (sobre un producto) ===")
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 2, "cantidad": 15})
check("POST venta Arroz x15 precio_total 4500", r.status_code == 201 and r.json()["precio_total"] == 4500, r.text)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 2, "cantidad": 2, "precio_total": 99999})
check("precio_total en body se ignora", r.status_code == 201 and r.json()["precio_total"] == 600, r.text)
r = req("GET", "/ventas/1")
j = r.json()
check(
    "GET venta/1 formato PDF (hora HH:MM, producto anidado, sin carrito)",
    r.status_code == 200 and j["hora"] == "10:30" and j["producto"]["nombre"] == "Arroz" and j["producto"]["precio"] == 300 and "carrito" not in j,
    r.text,
)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 99, "cantidad": 1})
check("POST venta producto inexistente 404", r.status_code == 404, r.text)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 1, "cantidad": 0})
check("POST venta cantidad 0 -> 422", r.status_code == 422, r.text)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30"})
check("POST venta sin modo -> 422", r.status_code == 422, r.text)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 1, "cantidad": 1, "id_carrito": 1})
check("POST venta con ambos modos -> 422", r.status_code == 422, r.text)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_producto": 1, "cantidad": 3})
check("POST venta Esponja x3 total 37.5", r.status_code == 201 and r.json()["precio_total"] == 37.5, r.text)
r = req("PUT", "/ventas/3", {"fecha": "2000-02-02", "hora": "11:00", "id_producto": 1, "cantidad": 4})
check("PUT venta/3 recalcula total 50", r.status_code == 200 and r.json()["precio_total"] == 50, r.text)

print("=== VERSION (1): ABM Carritos ===")
r = req("POST", "/carritos", {"fecha_creacion": "2000-01-02", "estado": "abierto"})
check("POST carrito abierto 201", r.status_code == 201 and r.json()["estado"] == "abierto", r.text)
r = req("POST", "/carritos", {"fecha_creacion": "2000-01-02", "estado": "encolado"})
check("POST carrito estado invalido 422", r.status_code == 422, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 2, "cantidad": 15})
check("POST carrito/1/productos Arroz x15", r.status_code == 201 and r.json()["cantidad"] == 15, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 2, "cantidad": 5})
check("producto repetido suma cantidad (20)", r.status_code == 201 and r.json()["cantidad"] == 20, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 1, "cantidad": 1})
check("agrega segundo producto", r.status_code == 201, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 99, "cantidad": 1})
check("agregar producto inexistente 404", r.status_code == 404, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 1, "cantidad": 0})
check("cantidad 0 -> 422", r.status_code == 422, r.text)
r = req("GET", "/carritos/1")
j = r.json()
check("GET carrito/1 con productos anidados", r.status_code == 200 and len(j["productos"]) == 2 and j["productos"][0]["producto"]["nombre"] == "Arroz", r.text)
r = req("PUT", "/carritos/1", {"estado": "cerrado"})
check("PUT cerrar carrito", r.status_code == 200 and r.json()["estado"] == "cerrado", r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 1, "cantidad": 1})
check("agregar a carrito cerrado 409", r.status_code == 409, r.text)
r = req("DELETE", "/carritos/1/productos/1")
check("quitar de carrito cerrado 409", r.status_code == 409, r.text)
req("POST", "/carritos", {"fecha_creacion": "2000-01-03", "estado": "abierto"})
req("POST", "/carritos/2/productos", {"id_producto": 1, "cantidad": 2})
r = req("DELETE", "/carritos/2/productos/1")
check("quitar producto de carrito abierto 200", r.status_code == 200, r.text)
r = req("DELETE", "/carritos/2/productos/50")
check("producto no esta en el carrito abierto 404", r.status_code == 404, r.text)
r = req("DELETE", "/productos/2")
check("no eliminar producto registrado en carrito 409", r.status_code == 409, r.text)

print("=== VERSION (1): Ventas con Carrito + reglas de negocio ===")
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_carrito": 1})
j = r.json()
venta_carrito_id = j.get("id")
check("POST venta con carrito cerrado 201, total 6012.5 (300x20 + 12.5x1)", r.status_code == 201 and j["precio_total"] == 6012.5, r.text)
r = req("GET", f"/ventas/{venta_carrito_id}")
j = r.json()
check(
    "GET venta con carrito anidado como ejemplo PDF",
    r.status_code == 200 and j["carrito"]["id"] == 1 and j["carrito"]["estado"] == "cerrado" and len(j["carrito"]["productos"]) == 2 and "producto" not in j,
    r.text,
)
r = req("POST", "/ventas", {"fecha": "2000-01-01", "hora": "10:30", "id_carrito": 1})
check("carrito ya asociado a otra venta 409", r.status_code == 409, r.text)
r = req("PUT", "/carritos/1", {"estado": "abierto"})
check("modificar carrito asignado 409", r.status_code == 409, r.text)
r = req("POST", "/carritos/1/productos", {"id_producto": 1, "cantidad": 1})
check("agregar producto a carrito asignado 409", r.status_code == 409, r.text)
r = req("DELETE", "/carritos/1")
check("eliminar carrito asignado 409", r.status_code == 409, r.text)
req("POST", "/carritos", {"fecha_creacion": "2000-01-04", "estado": "abierto"})
req("POST", "/carritos/3/productos", {"id_producto": 1, "cantidad": 1})
req("PUT", "/carritos/3", {"estado": "cerrado"})
r = req("POST", "/ventas", {"fecha": "2000-01-05", "hora": "09:00", "id_carrito": 3})
check("POST segunda venta con carrito 3", r.status_code == 201, r.text)
r = req("POST", f"/ventas/{venta_carrito_id}/carrito", {"id_carrito": 3})
check("asignar carrito ya usado en otra venta 409", r.status_code == 409, r.text)
r = req("POST", f"/ventas/{venta_carrito_id}/carrito", {"id_carrito": 99})
check("asignar carrito inexistente 404", r.status_code == 404, r.text)
r = req("PUT", f"/ventas/{venta_carrito_id}", {"id_producto": 2, "cantidad": 2})
check("PUT venta a modo directo: total 600 y sin carrito", r.status_code == 200 and r.json()["precio_total"] == 600 and "carrito" not in r.json(), r.text)
r = req("PUT", "/carritos/1", {"estado": "abierto"})
check("carrito desvinculado vuelve a ser modificable 200", r.status_code == 200, r.text)
req("PUT", "/carritos/1", {"estado": "cerrado"})
r = req("POST", f"/ventas/{venta_carrito_id}/carrito", {"id_carrito": 1})
check("POST /ventas/{{id}}/carrito reemplaza/conecta carrito cerrado", r.status_code == 200 and r.json()["carrito"]["id"] == 1, r.text)
r = req("GET", f"/ventas/{venta_carrito_id}")
check("venta ahora muestra carrito 1 y total recalculado 6012.5", r.status_code == 200 and r.json()["carrito"]["id"] == 1 and r.json()["precio_total"] == 6012.5, r.text)
r = req("DELETE", f"/ventas/{venta_carrito_id}")
check("DELETE venta 200", r.status_code == 200, r.text)
r = req("PUT", "/carritos/1", {"estado": "abierto"})
check("carrito libre tras DELETE de la venta", r.status_code == 200, r.text)
r = req("DELETE", "/carritos/1")
check("DELETE carrito libre 200", r.status_code == 200, r.text)
r = req("GET", "/carritos/1")
check("carrito eliminado 404", r.status_code == 404, r.text)

print()
print(f"RESULTADO: {pasados} PASS / {fallidos} FAIL")
sys.exit(1 if fallidos else 0)
