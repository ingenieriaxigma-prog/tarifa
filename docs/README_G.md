# 🧮 Microservicio G — Generación Eléctrica

> **Propósito:** Calcular el componente **G (Generación)** de la tarifa eléctrica, basado en precios reales de energía del mercado mayorista colombiano (XM).  
> Este microservicio obtiene datos en tiempo real, realiza el promedio ponderado de los precios y entrega un valor normalizado en $/kWh para su integración en la tarifa total.

---

## ⚙️ Arquitectura general

┌────────────────────────────┐
│ Cliente/API │
│ (tarifa_total_service) │
└────────────┬───────────────┘
│ POST /generacion/calcular
▼
┌──────────────────────┐
│ Microservicio G │
│ (FastAPI + asyncio) │
├──────────────────────┤
│ modelo.py │
│ logica.py │
│ main.py │
└───────┬──────────────┘
│
▼
┌──────────────────────────────┐
│ API pública XM (PBND) │
│ Precios de Bolsa │
│ PMD / PBND / Contratos │
└──────────────────────────────┘

yaml
Copiar código

---

## 📊 Flujo del cálculo

El componente **G** representa el **costo medio ponderado de generación**.  
Se calcula según la expresión:

G = Σ(Energia × Precio) / Σ(Energia)

yaml
Copiar código

donde:

| Símbolo | Descripción | Unidad |
|----------|--------------|--------|
| E        | Energía suministrada | kWh |
| P        | Precio unitario de energía | $/kWh |
| G        | Costo medio ponderado | $/kWh |

El sistema puede ponderar por planta, tipo de fuente o contrato.  
Cuando el valor no está disponible localmente, se consulta la API oficial de XM.

---

## 🌐 Fuente de datos XM

### Endpoint público (PBND)
La información de precios diarios promedio se obtiene desde el **Portal de Datos Abiertos de XM**:

https://apixm.xm.com.co/api/OfertasBolsa/PBND

cpp
Copiar código

**Ejemplo de respuesta (resumen):**
```json
{
  "data": [
    {
      "fecha": "2025-11-04",
      "precioBolsaNacional": 480.25,
      "precioBolsaRegional": {
        "andina": 482.10,
        "caribe": 479.00
      },
      "unidad": "$/kWh"
    }
  ]
}
🧠 Lógica del microservicio
El cálculo puede operar en dos modos:

Modo manual: recibe lista de contratos o compras con precios.

Modo automático: si un precio es 0 o None, se sustituye por el PBND actual obtenido de XM.

Esquema interno
mathematica
Copiar código
for compra in compras:
    if compra.precio_kWh is None or compra.precio_kWh == 0:
        compra.precio_kWh = obtener_precio_pbnd()
        
precio_ponderado = Σ(E*P) / Σ(E)
🧱 Estructura del servicio
bash
Copiar código
servicios/generacion/
├── modelo.py        # Esquemas Pydantic: CompraEnergia, ListaCompras
├── logica.py        # Cálculo ponderado, integración XM
├── main.py          # API FastAPI
└── Dockerfile       # Imagen del microservicio
📤 Ejemplo de uso
Request
bash
Copiar código
curl -X POST http://localhost:8001/generacion/calcular \
     -H "Content-Type: application/json" \
     -d '{
           "compras": [
             {"nombre": "Hidroeléctrica Betania", "energia_kWh": 5000, "precio_kWh": 420},
             {"nombre": "Térmica Cartagena", "energia_kWh": 2500, "precio_kWh": null}
           ]
         }'
Response
json
Copiar código
{
  "componente": "G",
  "fuente_datos": "XM PBND",
  "precio_promedio": 430.12,
  "total": 3225900.0,
  "detalle": [
    {"nombre": "Hidroeléctrica Betania", "energia_kWh": 5000, "precio_kWh": 420},
    {"nombre": "Térmica Cartagena", "energia_kWh": 2500, "precio_kWh": 482.1}
  ]
}
🔗 Integración con tarifa_total
El servicio tarifa_total_service realiza llamadas paralelas a los componentes:

csharp
Copiar código
async with httpx.AsyncClient() as client:
    resp_G = await client.post("http://generacion:8001/generacion/calcular", json=payload_G)
Si la API de XM falla, el sistema usa el valor de respaldo del config/normativa_config.json.

🧩 API Reference (OpenAPI style)
POST /generacion/calcular
Campo	Tipo	Descripción	Requerido
compras	array[CompraEnergia]	Lista de contratos o compras de energía	✅

Schema CompraEnergia

json
Copiar código
{
  "nombre": "string",
  "energia_kWh": 0,
  "precio_kWh": 0
}
Responses

Código	Descripción	Ejemplo
200	Cálculo exitoso	{"componente": "G", "precio_promedio": 430.12, ...}
400	Error en datos de entrada	{"detail": "El campo energia_kWh es obligatorio"}
500	Error interno o conexión XM	{"detail": "Error al consultar PBND de XM"}

🧪 Pruebas locales
1️⃣ Ejecutar solo el microservicio
bash
Copiar código
cd servicios/generacion
uvicorn main:app --reload --port 8001
2️⃣ Probar conexión XM
bash
Copiar código
curl http://localhost:8001/generacion/pbnd
3️⃣ Prueba completa de cálculo
bash
Copiar código
curl -X POST http://localhost:8001/generacion/calcular -H "Content-Type: application/json" -d @test_data.json
🐳 Despliegue en Docker
Dockerfile:

dockerfile
Copiar código
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core /app/core
COPY servicios/generacion /app/servicios/generacion
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "servicios.generacion.main:app", "--host", "0.0.0.0", "--port", "8001"]
Docker Compose:

yaml
Copiar código
generacion:
  build: ./servicios/generacion
  ports:
    - "8001:8001"
  volumes:
    - ./config:/app/config
🧭 Referencias técnicas
XM - Compañía de Expertos en Mercados: https://apixm.xm.com.co

CREG - Resolución 119 de 2007 y 101-072 de 2025

Documentación FastAPI: https://fastapi.tiangolo.com

✍️ Autor
Fabian González