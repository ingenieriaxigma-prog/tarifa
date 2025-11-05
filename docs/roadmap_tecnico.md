## ⚙️ Versión 1.0 — MVP Funcional (Actual)

> Objetivo: Implementar el sistema base de microservicios para cálculo tarifario, con arquitectura modular y consumo real de datos.

### 🧩 Backend
- ✅ Microservicio **G (Generación)** conectado a **API XM (PBND)**.  
- ✅ Microservicio **T (Transmisión)** con cargos CREG del STN.  
- 🚧 En progreso: microservicios **D, PR, R, C**.  
- ✅ `tarifa_total_service` orquestando llamadas asíncronas (`httpx.AsyncClient`).

### 🧠 Core
- ✅ `core/utils.py` y `core/calculadora.py` centralizados.  
- ✅ Lectura de `normativa_config.json`.  
- ✅ Estructura de respuesta estandarizada (JSON unificado).

### 🐳 Infraestructura
- ✅ Docker Compose con red interna (`tarifa_net`).  
- ✅ Servicios independientes con `uvicorn`.  
- ✅ Configuración de puertos 8000–8006.  

### 📚 Documentación
- ✅ README principal y técnicos (`README_G.md`, `README_T.md`, `README_TARIFA_TOTAL.md`).  
- ✅ Arquitectura general documentada.  
- 🚧 Pendiente: `docs/README_D.md`, `README_PR.md`, `README_R.md`, `README_C.md`.

---

## ⚙️ Versión 2.0 — Entorno Profesional (Próxima)

> Objetivo: Fortalecer la calidad, seguridad y automatización del ecosistema.

### 🧩 Backend
- 🧠 Agregar capa de **autenticación JWT** para todos los endpoints.  
- 🧩 Implementar **servicios restantes:** Distribución (D), Pérdidas (PR), Restricciones (R), Comercialización (C).  
- ⚙️ Añadir **endpoints de auditoría** (por componente y fecha).

### 🗄️ Base de datos
- 🧱 Implementar **PostgreSQL / Supabase**:
  - Tabla `historico_tarifas`
  - Tabla `version_normativa`
  - Tabla `detalle_componentes`
- 🔄 Registro automático de cada cálculo (`tarifa_total` guarda resultados).

### 🔐 Seguridad
- 🔑 JWT para autenticación de usuarios/microservicios.  
- 🧾 Roles: `admin`, `consultor`, `public`.  
- 🔒 HTTPS + gestión de claves en entorno seguro.

### ⚙️ DevOps / CI-CD
- 🚀 **GitHub Actions**:  
  - Test + Lint + Build en cada `push`.  
  - Publicación automática de imágenes en Docker Hub.  
- 🧰 **Pre-commit hooks**: flake8, black, isort, mypy.

### ☁️ Despliegue
- 🐳 Deploy en **AWS ECS / Fargate** o **Google Cloud Run**.  
- 🧭 Variables de entorno gestionadas por Secret Manager.  
- 🔁 Balanceador de carga (Application Load Balancer).

---

## ⚙️ Versión 3.0 — Plataforma Avanzada (Futuro)

> Objetivo: Evolucionar hacia una plataforma profesional, escalable y transparente.

### ⚡ Automatización Normativa
- 🤖 Servicio `creg_ingestor`: lectura automática de resoluciones CREG (PDF → JSON).  
- 🔄 Servicio `xm_ingestor`: actualización de precios diarios PBND desde XM API.  
- 🗂️ Versionado normativo: guardar cada actualización con fecha y metadatos.

### 📊 Datos y Auditoría
- 📈 Históricos por empresa, región y mes.  
- 📑 API de consulta pública `/tarifas/historico?fecha=...&componente=...`.  
- 🧮 Comparador de versiones normativas (CREG v2025-01 vs v2026-02).  

### 🧱 Infraestructura
- ☁️ Cluster Docker Swarm o Kubernetes (orquestación avanzada).  
- 📦 Servicios distribuidos por región.  
- 🧰 Observabilidad nativa (logs estructurados, métricas por componente).

### 💻 Frontend / UX
- 🌐 Dashboard interactivo con **Next.js / React**:  
  - Visualización de componentes tarifarios.  
  - Histórico, gráficos, análisis comparativos.  
- 📱 API pública con documentación OpenAPI + Swagger UI estilizado.

---

## 🧾 Hitos cumplidos ✅

| Área | Hito | Estado |
|------|------|--------|
| Backend | API de Generación conectada a XM | ✅ |
| Backend | Microservicio Transmisión funcional | ✅ |
| Orquestación | Cálculo total asíncrono (G + T) | ✅ |
| Infraestructura | Ecosistema Docker Compose estable | ✅ |
| Documentación | README generales y técnicos | ✅ |
| Core | Configuración normativa centralizada | ✅ |
| Backend | Validaciones de entrada y respuesta estándar | ✅ |
| Datos | Config preparada para PostgreSQL | 🕓 En diseño |
| Seguridad | Autenticación JWT | 🚧 Pendiente |
| CI/CD | GitHub Actions + Test suite | 🚧 Pendiente |
| Despliegue | Cloud ECS/Fargate | 🚧 Pendiente |
| Automatización | Ingestión regulatoria (CREG/XM) | 🚧 Pendiente |

---

## 🔄 Resumen ejecutivo

| Versión | Meta principal | Estado |
|----------|----------------|--------|
| v1.0 | MVP completo (G, T, Tarifa Total) | ✅ |
| v2.0 | Entorno profesional + DB + CI/CD | 🏗️ En planeación |
| v3.0 | Plataforma avanzada con automatización y dashboard | 🧭 En visión |

---

## ✍️ Autor

**Fabian González**  