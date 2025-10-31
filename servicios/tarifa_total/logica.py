import httpx
from servicios.tarifa_total.modelo import DatosEntrada, ResultadoTarifa


# URLs locales de los microservicios
SERVICIOS = {
    "generacion": "http://localhost:8001/calcular",
    "transmision": "http://localhost:8002/calcular",
    "distribucion": "http://localhost:8003/calcular",
    "perdidas_reconocidas": "http://localhost:8004/calcular",
    "restricciones": "http://localhost:8005/calcular",
    "comercializacion": "http://localhost:8006/calcular"
}

async def calcular_tarifa_total(datos: DatosEntrada) -> ResultadoTarifa:
    resultados = {}
    total = 0.0

    async with httpx.AsyncClient(timeout=10.0) as client:
        for nombre, url in SERVICIOS.items():
            try:
                respuesta = await client.post(url, json=datos.dict())
                respuesta.raise_for_status()
                data = respuesta.json()
                valor = data.get("valor") or data.get("valor_cop") or 0.0
                resultados[nombre] = round(valor, 2)
                total += valor
            except httpx.RequestError as e:
                resultados[nombre] = f"Error conexión: {e}"
            except httpx.HTTPStatusError as e:
                resultados[nombre] = f"Error respuesta: {e.response.status_code}"

    return ResultadoTarifa(
        componentes=resultados,
        tarifa_total=round(total, 2)
    )
