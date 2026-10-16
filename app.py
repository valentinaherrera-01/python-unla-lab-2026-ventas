from fastapi import FastAPI

app = FastAPI(
    title="API Ventas 2026",
    description="API REST para gestionar ventas de productos - Seminario de Lenguajes Python (UNLa)",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "API Ventas 2026 - Laboratorio Seminario de Lenguajes Python"}
