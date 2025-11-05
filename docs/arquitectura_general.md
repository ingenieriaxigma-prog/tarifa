# 🧩 Arquitectura General — Sistema de Cálculo de Tarifa Eléctrica

> **Propósito:** Documentar la arquitectura a nivel de microservicios del sistema de cálculo de tarifas eléctricas, describiendo la comunicación entre componentes, el flujo de datos, y la estructura modular del proyecto.

---

## ⚙️ Visión general

El sistema sigue una **arquitectura de microservicios desacoplados**, donde cada componente representa un **bloque regulatorio independiente** del esquema tarifario colombiano (CREG).

mathematica
Copiar código
     ┌──────────────────────────┐
     │        Usuario / API     │
     │  (cliente externo o web) │
     └──────────────┬───────────┘
                    │
                    ▼
         ┌─────────────────────────────┐
         │     tarifa_total_service     │
         │  (Orquestador principal)     │
         ├─────────────────────────────┤
         │ Llama a G, T, D, PR, R, C    │
         └───────────┬─────────────────┘
                     │
┌───────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
▼ ▼ ▼ ▼ ▼ ▼
│ G │ │ T │ │ D │ │ PR│ │ R │ │ C │
│ Generación │ Transmisión │ Distribución │ Pérdidas │ Restricciones│ Comercial. │
│ (XM API) │ (CREG STN) │ (STR/SDL) │ (XM Balance) │ (CREG 071/06)│ (Costos adm.)│
└───────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
│
▼
┌──────────────────────┐
│ Base de Datos (DB) │
│ PostgreSQL / Supabase│
│ (Histórico tarifas) │
└──────────────────────┘

yaml
Copiar código

---

## 🧱 Capas de la arquitectura

### 1️⃣ Core (núcleo común)
Ruta: `core/`

Contiene las funciones y utilidades compartidas entre todos los microservicios:
- `utils.py` → validaciones, redondeo, respuesta estándar.
- `calculadora.py` → carga de configuración normativa, funciones base de cálculo.
  
> **Objetivo:** mantener consistencia en formato, validaciones y trazabilidad.

---

### 2️⃣ Servicios (microservicios funcionales)
Ruta: `servicios/`

Cada microservicio se encarga de **un componente tarifario** regulado por la CREG.

| Servicio | Sigla | Fuente de datos | Propósito principal |
|-----------|--------|----------------|---------------------|
| `generacion` | G | API XM (PBND, PMD) | Cálculo de precio medio ponderado |
| `transmision` | T | CREG (STN) | Cargos por uso del sistema de transmisión nacional |
| `distribucion` | D | Operadores STR/SDL | Cargos por niveles de tensión |
| `perdidas_reconocidas` | PR | XM | Modela pérdidas energéticas |
| `restricciones` | R | XM + CREG 071/2006 | Costos marginales por congestión |
| `comercializacion` | C | Costos internos | Gastos de atención y margen comercial |
| `tarifa_total` | — | Todos los anteriores | Orquestador e integrador final |

---

### 3️⃣ Configuración normativa
Ruta: `config/normativa_config.json`

Archivo central con los parámetros de respaldo, cargos CREG y factores normativos.  
Cada microservicio lee esta información mediante `cargar_configuracion()` en `core/calculadora.py`.

**Ejemplo:**
```json
{
  "componente_T": {
    "cargos_por_nivel": { "1": 0.015, "2": 0.018, "3": 0.021 },
    "factor_geografico": { "costa": 1.0, "andina": 1.02 }
  },
  "componente_G": {
    "fuente": "XM API PBND",
    "valor_respaldo": 480.25
  }
}
4️⃣ Orquestador principal — tarifa_total_service
Responsable de:

Ejecutar consultas asíncronas a cada microservicio (httpx.AsyncClient).

Integrar los resultados y calcular la tarifa total.

Aplicar fallback automático si algún componente falla.

Retornar un JSON estándar con subtotales y total.

Ejemplo de flujo:

mathematica
Copiar código
1️⃣ Recibe consumo_kWh = 1000
2️⃣ Llama G, T, D, PR, R, C en paralelo
3️⃣ Espera respuestas → Suma totales
4️⃣ Devuelve tarifa total consolidada
5️⃣ Base de datos (futura)
Ruta: db/ (planeada)

Tecnología: PostgreSQL o Supabase.

Propósito: almacenamiento histórico, auditorías y trazabilidad de versiones normativas.

Tablas sugeridas:

historico_tarifas

version_normativa

detalle_componentes

usuarios (autenticación futura)

🔗 Flujo de datos (resumen)
css
Copiar código
Usuario → [tarifa_total_service] 
        → [G, T, D, PR, R, C]
        → [Core utils + Config]
        → [DB (histórico)]
        → Resultado JSON
🌐 Comunicación entre microservicios
Servicio	Endpoint interno	Puerto	Protocolo	Dependencias
Generación	http://generacion:8001/generacion/calcular	8001	HTTP	XM API
Transmisión	http://transmision:8002/transmision/calcular	8002	HTTP	Config local
Distribución	http://distribucion:8003/distribucion/calcular	8003	HTTP	Config local
Pérdidas reconocidas	http://perdidas_reconocidas:8004/perdidas/calcular	8004	HTTP	XM
Restricciones	http://restricciones:8005/restricciones/calcular	8005	HTTP	XM
Comercialización	http://comercializacion:8006/comercializacion/calcular	8006	HTTP	Config local
Tarifa total	http://tarifa_total:8000/tarifa/calcular	8000	HTTP	Todos los anteriores

🧩 Red Docker (vista simplificada)
csharp
Copiar código
[Docker Network: tarifa_net]
     ├── generacion:8001
     ├── transmision:8002
     ├── distribucion:8003
     ├── perdidas_reconocidas:8004
     ├── restricciones:8005
     ├── comercializacion:8006
     └── tarifa_total:8000
Cada contenedor se comunica internamente usando su nombre de servicio (no IP).
Todos comparten el volumen /config y el entorno PYTHONPATH=/app.

⚙️ Flujo de ejecución completo
bash
Copiar código
1️⃣ Usuario envía POST /tarifa/calcular
2️⃣ tarifa_total recibe consumo_kWh
3️⃣ Ejecuta llamadas en paralelo a G, T, D, PR, R, C
4️⃣ Cada microservicio usa config/normativa_config.json
5️⃣ Respuestas agregadas → cálculo final
6️⃣ Retorna JSON con subtotales + tarifa total
🐳 Tabla de puertos Docker
Servicio	Puerto interno	Puerto expuesto	Descripción
Generación	8001	8001	Cálculo G (XM API)
Transmisión	8002	8002	Cálculo T (CREG)
Distribución	8003	8003	Cálculo D
Pérdidas Reconocidas	8004	8004	Cálculo PR
Restricciones	8005	8005	Cálculo R
Comercialización	8006	8006	Cálculo C
Tarifa Total	8000	8000	Orquestador general

⚙️ Despliegue local (modo desarrollo)
bash
Copiar código
# Construir todos los servicios
docker compose build --no-cache

# Iniciar ecosistema completo
docker compose up
Verifica con:

bash
Copiar código
curl http://localhost:8000/tarifa/health
☁️ Despliegue en nube (visión general)
Infraestructura:

AWS ECS / Fargate o Google Cloud Run (contenedores gestionados).

Configuración externa:

Variables de entorno en Secret Manager.

Almacenamiento persistente para la base de datos (RDS o Supabase).

Escalabilidad:

Cada microservicio puede escalar horizontalmente según carga.

tarifa_total actúa como gateway lógico.

📘 Resumen de diseño
Capa	Propósito	Ejemplo
Core	Lógica compartida	redondear(), respuesta_estandar()
Config	Parámetros normativos	normativa_config.json
Servicios	Cálculo por componente	G, T, D, PR, R, C
Orquestador	Integración total	tarifa_total
Base de datos	Histórico de resultados	PostgreSQL / Supabase

✍️ Autor
Fabian González