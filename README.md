# Laboratorio 2026 - Ventas

API REST para gestión de ventas de productos, desarrollada para el **Seminario de Lenguajes Python** (Licenciatura en Sistemas - UNLa), año de cursada 2026.

## Integrantes

- Valentina Herrera ([@valentinaherrera-01](https://github.com/valentinaherrera-01))

## Funcionalidades

| Funcionalidad | Branch | Descripción |
|---|---|---|
| ABM de Productos | `valentinaherrera-01-abmProductos` | Alta, baja, listado y modificación de productos |
| ABM de Ventas | `valentinaherrera-01-abmVentas` | Ventas sobre un sólo producto con cálculo de precio total |
| ABM de Carritos | `valentinaherrera-01-abmCarritos` | Carritos de compras que agrupan productos con sus cantidades |
| Ventas con Carrito | `valentinaherrera-01-ventasConCarrito` | Asociación venta ↔ carrito (1 a 1) y reglas de negocio |

## Stack tecnológico

- Python 3
- FastAPI
- SQLite
- SQLAlchemy
- Pandas
- Borb

## Instalación y ejecución

- Abrir PowerShell/Bash/Terminal y navegar a la carpeta del proyecto.
- Ejecutar `python -m venv .venv` para crear el entorno virtual.
- Ejecutar `.venv/Scripts/activate` (Windows) para activar el venv.
- Ejecutar `pip install -r requirements.txt` para instalar las librerías del archivo requirements.
- Ejecutar `fastapi run` para levantar la aplicación en `localhost:8000`.
- Abrir el navegador en `localhost:8000/docs` para ver la documentación Swagger.

## Endpoints

### Productos

| Verbo | Ruta | Descripción |
|---|---|---|
| POST | `/productos` | Crea un producto `{ "nombre": "Esponja", "precio": 11.11 }` |
| GET | `/productos` | Listado de productos |
| GET | `/productos/{id}` | Obtiene un producto |
| PUT | `/productos/{id}` | Actualiza un producto |
| DELETE | `/productos/{id}` | Elimina un producto (no si está registrado en un carrito) |

### Ventas (sobre un sólo producto o con carrito)

| Verbo | Ruta | Descripción |
|---|---|---|
| POST | `/ventas` | Crea una venta: `{ "fecha", "hora", "id_producto", "cantidad" }` **o** `{ "fecha", "hora", "id_carrito" }` |
| GET | `/ventas` | Listado de ventas |
| GET | `/ventas/{id}` | Obtiene una venta con su producto o carrito anidado |
| PUT | `/ventas/{id}` | Actualiza una venta (recalcula `precio_total`) |
| DELETE | `/ventas/{id}` | Elimina una venta (libera su carrito) |
| POST | `/ventas/{id}/carrito` | Asigna o reemplaza el carrito de una venta `{ "id_carrito": 1 }` |

> `precio_total` nunca se recibe en el body: lo calcula la API (precio unitario × cantidad, o suma de los productos del carrito).

### Carritos

| Verbo | Ruta | Descripción |
|---|---|---|
| POST | `/carritos` | Crea un carrito `{ "fecha_creacion": "2000-01-02", "estado": "abierto" }` |
| GET | `/carritos` | Listado de carritos |
| GET | `/carritos/{id}` | Obtiene un carrito con sus productos |
| PUT | `/carritos/{id}` | Actualiza un carrito (no si está asociado a una venta) |
| DELETE | `/carritos/{id}` | Elimina un carrito y sus productos (no si está asociado a una venta) |
| POST | `/carritos/{id}/productos` | Agrega un producto `{ "id_producto": 2, "cantidad": 15 }` (si ya existe, suma la cantidad) |
| DELETE | `/carritos/{id}/productos/{id_producto}` | Quita un producto del carrito |

## Reglas de negocio implementadas

- **Ventas**: el body de `POST /ventas` y `PUT /ventas/{id}` nunca recibe `precio_total`; para registrar una venta o asignar un carrito, el carrito debe existir, no estar asociado a otra venta y estar en estado `"cerrado"`.
- **Carritos**: sólo se agregan o quitan productos de un carrito `"abierto"`; el `id_producto` debe existir y encontrarse en el carrito; la cantidad debe ser mayor a 0; un carrito asociado a una venta no puede ser modificado, reabierto ni eliminado.
- **Productos**: no se puede eliminar un producto registrado en algún carrito.

## Tests

- `tests_e2e.py`: tests end-to-end que cubren los ejemplos de ambos PDFs y todas las reglas de negocio (49 aserciones).
- Con la aplicación levantada, ejecutar: `python tests_e2e.py` (o `API_BASE=http://localhost:8030 python tests_e2e.py` si corre en otro puerto).

## Base de datos

- `database.db`: archivo SQLite generado automáticamente al levantar la aplicación por primera vez.
- Puede inspeccionarse con [DB Browser for SQLite](https://sqlitebrowser.org/).
