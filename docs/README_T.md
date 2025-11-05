# ⚡ Microservicio T — Transmisión Eléctrica

> **Propósito:** Calcular el componente **T (Transmisión)** de la tarifa eléctrica, aplicando los cargos regulados del **Sistema de Transmisión Nacional (STN)** definidos por la **CREG**, con factores geográficos y horarios ajustables desde configuración.

---

## ⚙️ Arquitectura general

┌────────────────────────────┐
│ Cliente/API │
│ (tarifa_total_service) │
└────────────┬───────────────┘
│ POST /transmision/calcular
▼
┌──────────────────────┐
│ Microservicio T │
│ (FastAPI + asyncio) │
├──────────────────────┤
│ modelo.py │
│ logica.py │
│ main.py │
└───────┬──────────────┘
│
▼
┌──────────────────────────────┐
│ config/normativa_config.json │
│ (Cargos CREG + Factores) │
└──────────────────────────────┘

yaml
Copiar código

---

## 📊 Flujo del cálculo

El componente **T** corresponde al costo de uso del **Sistema de Transmisión Nacional (STN)**, regulado por la **CREG**.  
Su cálculo considera el nivel de tensión, la energía transportada y los factores regionales.

Fórmula base:

T_total = Σ [ E_i × CU_i × FG_i × FH_i ]

yaml
Copiar código

donde:

| Símbolo | Descripción | Unidad |
|----------|--------------|--------|
| E_i | Energía del tramo o línea i | kWh |
| CU_i | Cargo unitario del nivel de tensión i | $/kWh |
| FG_i | Factor geográfico (por región) | adimensional |
| FH_i | Factor horario (por franja horaria) | adimensional |
| T_total | Costo total de transmisión | $ |

---

## 🧱 Estructura del servicio

servicios/transmision/
├── modelo.py # Esquemas de entrada (niveles de tensión, energía, etc.)
├── logica.py # Cálculo T_total = Σ(E×CU×FG×FH)
├── main.py # Endpoints FastAPI
└── Dockerfile # Imagen del microservicio

yaml
Copiar código

---

## ⚙️ Ejemplo de configuración (`normativa_config.json`)

```json
{
  "componente_T": {
    "cargos_por_nivel": {
      "1": 0.0152,
      "2": 0.0178,
      "3": 0.0204,
      "4": 0.0231
    },
    "factor_geografico": {
      "costa": 1.00,
      "andina": 1.02,
      "amazonica": 1.03
    },
    "recargo_horario": {
      "pico": 1.05,
      "valle": 0.95,
      "llano": 1.00
    }
  }
}
El microservicio lee estos valores desde core/calculadora.cargar_configuracion() para aplicar automáticamente los cargos según el nivel y región.

🧠 Flujo interno del cálculo
css
Copiar código
for linea in lineas:
    CU = cargo_por_nivel(nivel_tension)
    FG = factor_geografico(region)
    FH = recargo_horario(franja_horaria)
    subtotal = energia_kWh * CU * FG * FH
    acumular subtotal
Diagrama ASCII de flujo
java
Copiar código
┌──────────────┐
│  Entrada     │
│ (lineas[])   │
└──────┬───────┘
       ▼
┌───────────────────────────────┐
│ Lee cargos_por_nivel del JSON │
└──────────┬────────────────────┘
           ▼
┌────────────────────────────────────────┐
│ Calcula subtotal = E × CU × FG × FH     │
└──────────┬──────────────────────────────┘
           ▼
┌───────────────────────────┐
│ Suma subtotales → T_total │
└───────────────────────────┘
📤 Ejemplo de uso
Request
bash
Copiar código
curl -X POST http://localhost:8002/transmision/calcular \
     -H "Content-Type: application/json" \
     -d '{
           "lineas": [
             {"nivel_tension": 3, "energia_kWh": 12000},
             {"nivel_tension": 4, "energia_kWh": 8000, "region": "costa", "franja_horaria": "pico"}
           ]
         }'
Response
json
Copiar código
{
  "componente": "T",
  "total": 420.87,
  "detalle": [
    {
      "linea": 1,
      "nivel_tension": 3,
      "energia_kWh": 12000,
      "cargo_base_kWh": 0.0204,
      "factor": 1.0,
      "subtotal": 244.8
    },
    {
      "linea": 2,
      "nivel_tension": 4,
      "energia_kWh": 8000,
      "cargo_base_kWh": 0.0231,
      "factor": 1.05,
      "subtotal": 176.07
    }
  ]
}
🔗 Integración con tarifa_total
El servicio tarifa_total_service consulta el microservicio T de manera asíncrona junto con los demás componentes.

python
Copiar código
resp_T = await client.post("http://transmision:8002/transmision/calcular", json=_payload_transmision())
El valor resp_T["total"] se incorpora al cálculo global de la tarifa eléctrica.

🧩 API Reference (OpenAPI style)
POST /transmision/calcular
Campo	Tipo	Descripción	Requerido
lineas	array[LineaTransmision]	Lista de tramos o líneas a evaluar	✅

Schema LineaTransmision

json
Copiar código
{
  "nivel_tension": 1,
  "energia_kWh": 0,
  "cargo_uso_kWh": 0,
  "region": "string",
  "franja_horaria": "pico | valle | llano"
}
Responses

Código	Descripción	Ejemplo
200	Cálculo exitoso	{"componente": "T", "total": 420.87, "detalle": [...]}
400	Error de validación	{"detail": "nivel_tension fuera de rango"}
500	Error interno	{"detail": "Error al leer configuración"}

⚠️ Validaciones y errores comunes
Error detectado	Causa probable	Solución
nivel_tension fuera de rango	Valor no entre 1–4	Verificar dato de entrada
energia_kWh <= 0	Energía nula o negativa	Corregir medición o entrada
region desconocida	Región no definida en factor_geografico	Agregar valor en config
franja_horaria no válida	Solo acepta pico, valle o llano	Ajustar dato de entrada
Error al leer configuración	Falta o formato inválido de JSON	Validar archivo normativa_config.json

🧪 Pruebas locales
1️⃣ Ejecutar el servicio
bash
Copiar código
cd servicios/transmision
uvicorn main:app --reload --port 8002
2️⃣ Health check
bash
Copiar código
curl http://localhost:8002/transmision/health
3️⃣ Cálculo manual
bash
Copiar código
curl -X POST http://localhost:8002/transmision/calcular -H "Content-Type: application/json" -d @test_lineas.json
🐳 Despliegue con Docker
Dockerfile:

dockerfile
Copiar código
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core /app/core
COPY servicios/transmision /app/servicios/transmision
COPY config /app/config
ENV PYTHONPATH=/app
EXPOSE 8002
CMD ["uvicorn", "servicios.transmision.main:app", "--host", "0.0.0.0", "--port", "8002"]
Docker Compose:

yaml
Copiar código
transmision:
  build: ./servicios/transmision
  ports:
    - "8002:8002"
  volumes:
    - ./config:/app/config
  depends_on:
    - generacion
🧭 Referencias técnicas
CREG — Resoluciones 119/2007 y 101-072/2025 (Cargos STN vigentes).

XM — Datos públicos de pérdidas y factores de red.

FastAPI — Framework base: https://fastapi.tiangolo.com

✍️ Autor
Fabian González