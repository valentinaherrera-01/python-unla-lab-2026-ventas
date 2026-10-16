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

## Base de datos

- `database.db`: archivo SQLite generado automáticamente al levantar la aplicación por primera vez.
- Puede inspeccionarse con [DB Browser for SQLite](https://sqlitebrowser.org/).
