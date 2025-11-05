# Sistema de Cálculo de Tarifa Eléctrica (Arquitectura General)

> Proyecto desarrollado por **Fabian González** — Arquitectura modular basada en microservicios para el cálculo profesional de la tarifa eléctrica en Colombia, siguiendo modelos similares a los empleados por XM, Air-e y Enel.

---

## Visión General

El proyecto implementa un **ecosistema de microservicios FastAPI** orquestados mediante **Docker Compose**, cada uno encargado de calcular un **componente tarifario independiente**, tal como lo establece la **regulación CREG**.

Los componentes se comunican de forma **asíncrona vía HTTP interno**, y el servicio `tarifa_total` integra todos los resultados parciales para obtener la tarifa final aplicada a un consumo determinado.

---

## Arquitectura del Sistema

### 1. Componentes principales

| Microservicio                 | Fuente de datos                                  | Cálculo principal                                                         |
| ----------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------- |
| **G - Generación**            | API XM (PBND, PMD, contratos, fuentes de planta) | Costo medio ponderado Σ(E×P)/Σ(E)                                         |
| **T - Transmisión**           | Cargos CREG del STN                              | Aplicación de cargos por nivel de tensión y factores geográficos/horarios |
| **D - Distribución**          | Datos del STR/SDL                                | Cargos regulados según tensión y tramos de red                            |
| **PR - Pérdidas reconocidas** | Balance energético (XM)                          | Diferencia entre pérdidas reales y reconocidas                            |
| **R - Restricciones**         | Resolución CREG 071/2006                         | Costo marginal por generación adicional en zonas congestionadas           |
| **C - Comercialización**      | Datos internos del comercializador               | Gastos administrativos, atención, margen, etc.                            |
| **tarifa_total**              | Integración de todos los anteriores              | Cálculo final de tarifa total ($/kWh)                                     |

---

### 2. Arquitectura en capas

```
📂 tarifa-electrica/
├── core/                # Utilidades y funciones compartidas
│   ├── utils.py         # redondear(), respuesta_estandar(), validaciones
│   └── calculadora.py   # cargar_configuracion(), cálculos comunes
│
├── servicios/
│   ├── generacion/      # Cálculo G - Integrado con XM
│   ├── transmision/     # Cálculo T - Implementación profesional
│   ├── distribucion/    # (En procceso)
│   ├── perdidas_reconocidas/
│   ├── restricciones/
│   ├── comercializacion/
│   └── tarifa_total/    # Orquestador principal
│
├── config/
│   └── normativa_config.json   # Parámetros normativos y valores de respaldo
│
├── docker-compose.yml   # Orquestación de servicios
├── Dockerfile           # Imagen base del proyecto
└── requirements.txt     # Dependencias compartidas
```

Cada microservicio incluye su propio `main.py`, `logica.py`, `modelo.py` y `Dockerfile`, lo que permite su **despliegue independiente o conjunto**.

---

## Flujo de Cálculo (E2E)

1. El usuario (o sistema externo) invoca el endpoint principal en `tarifa_total`:

   ```http
   POST /tarifa/calcular
   ```
2. `tarifa_total` consulta, en paralelo, los microservicios `G`, `T`, `D`, `PR`, `R`, `C`.
3. Cada microservicio devuelve un **JSON estandarizado** con su valor total y detalle.
4. `tarifa_total` suma y consolida la tarifa final en función del consumo.

---

## Principios de Diseño

* **Desacoplamiento total:** cada componente tiene su propia API y lógica.
* **Configuración centralizada:** `normativa_config.json` almacena parámetros regulados.
* **Escalabilidad horizontal:** cada microservicio puede escalarse individualmente.
* **Resiliencia:** `tarifa_total` usa llamadas asíncronas con `tenacity` para reintentos.
* **Portabilidad:** 100% Docker; puede desplegarse localmente o en la nube (AWS ECS, GCP, etc.).

---

## 🧪 Ejemplo de uso local

### 1 Construir e iniciar todos los servicios

```bash
docker compose up --build
```

### 2️ Verificar salud

```bash
curl http://localhost:8001/generacion/health
curl http://localhost:8002/transmision/health
```

### 3️ Probar cálculo individual (Transmisión)

```bash
curl -X POST http://localhost:8002/transmision/calcular \
  -H 'Content-Type: application/json' \
  -d '{
        "lineas": [
          {"nivel_tension": 3, "energia_kWh": 12000},
          {"nivel_tension": 4, "energia_kWh": 8000, "region": "costa", "franja_horaria": "pico"}
        ]
      }'
```

### 4️ Calcular tarifa total

```bash
curl -X POST http://localhost:8000/tarifa/calcular -H 'Content-Type: application/json' -d '{"consumo_kWh": 1000}'
```

---

## Tecnologías principales

| Componente             | Tecnología                                        |
| ---------------------- | ------------------------------------------------- |
| Framework web          | **FastAPI**                                       |
| Concurrencia           | **asyncio** + **httpx**                           |
| Orquestación           | **Docker Compose**                                |
| Base de datos (futura) | PostgreSQL / Supabase (planificado)               |
| Configuración          | JSON + Variables de entorno                       |
| Logs                   | Python `logging` + JSON estructurado (en roadmap) |

---

## Ejemplo de respuesta estándar

```json
{
  "ok": true,
  "mensaje": "Cálculo exitoso",
  "datos": {
    "componente": "T",
    "total": 0.3215,
    "detalle": [ { ... } ]
  },
  "timestamp": "2025-11-05T07:45:00"
}
```

---

## Roadmap Técnico

1. ✅ Conectar **G** (Generación) con API XM.
2. ✅ Desarrollar **T** (Transmisión) con cargos CREG y factores regionales.
3. 🚧 Crear **D**, **PR**, **R**, **C** siguiendo la misma plantilla.
4. 📊 Integrar dashboard de monitoreo con Prometheus + Grafana.
5. ☁️ Desplegar en contenedor ECS/Fargate o Google Cloud Run.
6. 🔐 Añadir autenticación JWT para servicios externos.
7. 📂 Implementar versionado normativo (`/version` endpoint).

---

## 👨‍💻 Autor

**MASA ING**
