# ⚙️ Microservicio TARIFA_TOTAL — Integrador de Componentes Tarifarios

> **Propósito:** Centralizar la comunicación entre los microservicios **G, T, D, PR, R, C**  
> para calcular la **tarifa eléctrica total ($/kWh)** aplicada a un consumo determinado.  
> Este servicio coordina las llamadas asíncronas, combina los resultados y entrega un  
> resumen completo con trazabilidad por componente.

---

## 🧩 Arquitectura general

css
Copiar código
             ┌──────────────────────────────┐
             │  Usuario / Cliente externo   │
             └──────────────┬───────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Microservicio        │
                 │  tarifa_total        │
                 │  (FastAPI + httpx)   │
                 ├──────────────────────┤
                 │  clients.py          │
                 │  calculadora.py      │
                 │  main.py             │
                 └────────┬─────────────┘
                          │
   ┌──────────────────────┼────────────────────────┐
   ▼                      ▼                        ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Generación │ │ Transmisión │ ... │ Comercialización │
│ (G) │ │ (T) │ │ (C) │
└──────────────┘ └──────────────┘ └──────────────┘

yaml
Copiar código

Cada componente se ejecuta como microservicio independiente dentro de **Docker Compose**,  
y `tarifa_total` actúa como **API orquestadora** de alto nivel.

---

## ⚙️ Flujo del cálculo general

Fórmula base de la tarifa eléctrica final:

Tarifa_Total = (G + T + D + PR + R + C)

yaml
Copiar código

> Donde cada letra representa el valor total entregado por su respectivo microservicio.

El servicio:
1. Recibe el **consumo total (kWh)** como parámetro.
2. Llama a cada microservicio usando `httpx.AsyncClient` en paralelo.
3. Espera las respuestas JSON.
4. Aplica redondeos y suma los resultados.
5. Devuelve un JSON consolidado con los subtotales y el total final.

---

## 🧠 Flujo lógico interno

async def calcular_tarifa_total_automatica(consumo_kWh):
componentes = await obtener_componentes_en_paralelo()
resultado = {
"G": resp_G["total"],
"T": resp_T["total"],
"D": resp_D["total"],
"PR": resp_PR["total"],
"R": resp_R["total"],
"C": resp_C["total"]
}
total = sum(resultado.values())
return {"total": total, "detalle": resultado}

yaml
Copiar código

---

## 🧱 Estructura del servicio

servicios/tarifa_total/
├── main.py # Endpoints FastAPI
├── clients.py # Conexiones HTTP a G, T, D, PR, R, C
├── core_utils.py # Validaciones, respuesta estándar
├── calculadora.py # Lógica general de cálculo
├── Dockerfile # Imagen del microservicio
└── tests/ # Pruebas de integración

yaml
Copiar código

---

## 🌐 Dependencias de red (Docker Compose)

```yaml
services:
  tarifa_total:
    build: ./servicios/tarifa_total
    ports:
      - "8000:8000"
    depends_on:
      - generacion
      - transmision
      - distribucion
      - perdidas_reconocidas
      - restricciones
      - comercializacion
Todos los microservicios deben estar activos antes de ejecutar tarifa_total.

📤 Ejemplo de uso
Request
bash
Copiar código
curl -X POST http://localhost:8000/tarifa/calcular \
     -H "Content-Type: application/json" \
     -d '{"consumo_kWh": 1000}'
Response
json
Copiar código
{
  "ok": true,
  "mensaje": "Cálculo exitoso",
  "datos": {
    "detalle": {
      "G": 430.12,
      "T": 420.87,
      "D": 350.55,
      "PR": 10.22,
      "R": 8.91,
      "C": 40.00
    },
    "total_tarifa": 1260.67
  },
  "timestamp": "2025-11-05T10:32:00"
}
🔗 Comunicación entre microservicios
bash
Copiar código
tarifa_total ──► generacion:8001/generacion/calcular
             ├─► transmision:8002/transmision/calcular
             ├─► distribucion:8003/distribucion/calcular
             ├─► perdidas_reconocidas:8004/perdidas/calcular
             ├─► restricciones:8005/restricciones/calcular
             └─► comercializacion:8006/comercializacion/calcular
Cada llamada se realiza con timeout configurable (5–10s) y reintentos automáticos.

⚙️ Manejo de fallos
El sistema implementa resiliencia básica:

Si un microservicio no responde, se usa su valor de respaldo en config/normativa_config.json.

El campo detalle indica qué fuentes se usaron en cada caso.

Ejemplo de respuesta con fallback:

json
Copiar código
{
  "detalle": {
    "G": {"valor": 430.12, "fuente": "XM"},
    "T": {"valor": 420.87, "fuente": "CREG"},
    "D": {"valor": 0.0, "fuente": "Respaldo local (config)"}
  }
}
🧩 API Reference (OpenAPI style)
POST /tarifa/calcular
Campo	Tipo	Descripción	Requerido
consumo_kWh	number	Consumo total en kWh	✅

Responses

Código	Descripción	Ejemplo
200	Cálculo exitoso	{"ok": true, "datos": {"total_tarifa": 1260.67, ...}}
400	Error de validación	{"detail": "El consumo debe ser mayor a 0 kWh"}
500	Error interno o conexión fallida	{"detail": "Error al conectar con G o T"}

⚠️ Validaciones y errores comunes
Error	Causa	Solución
Conexión fallida	Microservicio inactivo	Revisar docker compose ps
Timeout al obtener componentes	Llamada bloqueada o lenta	Aumentar tiempo de espera en clients.py
Formato inválido	JSON mal estructurado	Validar estructura antes del envío
consumo_kWh <= 0	Entrada errónea	Corregir valor de consumo

🧪 Pruebas locales
1️⃣ Iniciar todos los servicios
bash
Copiar código
docker compose up --build
2️⃣ Verificar salud
bash
Copiar código
curl http://localhost:8000/tarifa/health
3️⃣ Ejecutar prueba completa
bash
Copiar código
curl -X POST http://localhost:8000/tarifa/calcular -H "Content-Type: application/json" -d '{"consumo_kWh": 500}'
🐳 Dockerfile
dockerfile
Copiar código
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core /app/core
COPY servicios/tarifa_total /app/servicios/tarifa_total
COPY config /app/config
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "servicios.tarifa_total.main:app", "--host", "0.0.0.0", "--port", "8000"]
📈 Ejemplo de salida extendida (modo debug)
json
Copiar código
{
  "ok": true,
  "mensaje": "Cálculo exitoso (modo depuración)",
  "datos": {
    "detalle": {
      "G": {"total": 430.12, "status": "ok"},
      "T": {"total": 420.87, "status": "ok"},
      "D": {"status": "error", "detalle": "Falla conexión"},
      "PR": {"total": 10.22, "status": "ok"},
      "R": {"total": 8.91, "status": "ok"},
      "C": {"total": 40.00, "status": "ok"}
    },
    "tarifa_total": 910.12
  },
  "fuentes": ["XM", "CREG", "config_local"]
}
🧭 Referencias técnicas
CREG — Resoluciones 119/2007, 101-072/2025 (estructura tarifaria).

XM — Datos públicos de generación y restricciones.

FastAPI — Framework base: https://fastapi.tiangolo.com

✍️ Autor
Fabian González