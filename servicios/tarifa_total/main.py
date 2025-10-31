from fastapi import FastAPI
import httpx

app = FastAPI(title="Tarifa Total Service", version="1.0")

# Endpoints de los microservicios dentro de la red Docker Compose
SERVICES = {
    "generacion": "http://tarifa-electrica-generacion:8001/valor",
    "transmision": "http://tarifa-electrica-transmision:8002/valor",
    "distribucion": "http://tarifa-electrica-distribucion:8003/valor",
    "perdidas_reconocidas": "http://tarifa-electrica-perdidas_reconocidas:8004/valor",
    "restricciones": "http://tarifa-electrica-restricciones:8005/valor",
    "comercializacion": "http://tarifa-electrica-comercializacion:8006/valor",
}

@app.get("/")
def root():
    return {"message": "Servicio de Tarifa Total activo"}

@app.get("/tarifa_total")
async def calcular_tarifa_total():
    resultados = {}
    total = 0

    async with httpx.AsyncClient(timeout=5.0) as client:
        for nombre, url in SERVICES.items():
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()

                # Cada servicio debería devolver {"valor": X}
                valor = data.get("valor", 0)
                resultados[nombre] = {"estado": "ok", "valor": valor}
                total += valor

            except httpx.RequestError as e:
                resultados[nombre] = {"estado": "error", "detalle": f"Conexión fallida: {e}"}
            except httpx.HTTPStatusError as e:
                resultados[nombre] = {"estado": "error", "detalle": f"HTTP {e.response.status_code}: {e.response.text}"}
            except Exception as e:
                resultados[nombre] = {"estado": "error", "detalle": str(e)}

    return {
        "detalle": resultados,
        "tarifa_total": total
    }
