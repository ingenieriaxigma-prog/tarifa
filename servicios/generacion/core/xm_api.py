import httpx
from datetime import date, timedelta
from core.calculadora import cargar_configuracion

BASE_URL = "https://servapibi.xm.com.co"
TIMEOUT = 30.0
_metricas_cache = {"items": None}


async def _post(path: str, payload: dict):
    """Envía una solicitud POST al endpoint de XM."""
    url = f"{BASE_URL}{path}"
    print(f"🌐 Enviando POST a {url} con payload={payload}")
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"📩 Respuesta HTTP {r.status_code}: {r.text[:300]}...")
        if r.status_code >= 400:
            detalle = r.text.strip() if r.text else ""
            raise RuntimeError(f"XM API devolvió {r.status_code}: {detalle}")
        return r.json()


async def listar_metricas_xm(force: bool = False):
    """Consulta el inventario de métricas en XM (/lists)."""
    global _metricas_cache
    if not force and _metricas_cache["items"] is not None:
        return _metricas_cache["items"]

    payload = {"MetricId": "ListadoMetricas"}
    resp_json = await _post("/lists", payload)
    print(f"📘 Respuesta XM /lists recibida (keys={list(resp_json.keys())})")

    data = resp_json.get("Data") or resp_json.get("data") or resp_json.get("List") or []
    metricas = []
    for item in data:
        m = {
            "MetricId": item.get("MetricId") or item.get("Codigo"),
            "MetricName": item.get("MetricName") or item.get("NombreMetrica"),
            "Entity": item.get("Entity") or item.get("Desagregacion"),
            "Type": item.get("Type") or item.get("Tipo"),
            "Url": item.get("Url") or item.get("URL"),
            "MetricUnits": item.get("MetricUnits") or item.get("Unidades"),
            "Raw": item,
        }
        metricas.append(m)

    _metricas_cache["items"] = metricas
    print(f"✅ Total métricas cargadas: {len(metricas)}")
    return metricas


def _pick_metric_precio_bolsa(metricas: list):
    """Selecciona la métrica más probable del Precio Bolsa Nacional."""
    if not metricas:
        return None

    for m in metricas:
        mid = str(m.get("MetricId") or "").lower()
        if mid in ["ppprecbolsnaci", "precbolsnaci"]:
            print(f"🎯 Métrica detectada por ID: {mid}")
            return m

    for m in metricas:
        nombre = str(m.get("MetricName") or "").lower()
        if "precio" in nombre and "bolsa" in nombre and "nacional" in nombre:
            print(f"🎯 Métrica detectada por nombre: {nombre}")
            return m
    print("⚠️ No se encontró una métrica PBND explícita")
    return None


async def obtener_precio_bolsa_xm():
    """
    Obtiene el Precio Bolsa Nacional Diario desde XM, retrocediendo días si el resultado viene vacío.
    Devuelve una tupla (valor, fuente), donde la fuente puede ser 'XM' o 'Respaldo local (config.json)'.
    """
    try:
        print("🚀 Iniciando consulta del Precio Bolsa Nacional a XM...")
        metricas = await listar_metricas_xm()
        m = _pick_metric_precio_bolsa(metricas)
        metric_id = m.get("MetricId", "PPPrecBolsNaci") if m else "PPPrecBolsNaci"

        dias_retroceso = 0
        valor = None

        while dias_retroceso < 5 and valor is None:  # hasta 5 días atrás
            end_d = date.today() - timedelta(days=dias_retroceso)
            start_d = end_d - timedelta(days=3)
            print(f"📅 Intento {dias_retroceso+1}: rango {start_d} → {end_d}")

            payload = {
                "MetricId": metric_id,
                "StartDate": start_d.strftime("%Y-%m-%d"),
                "EndDate": end_d.strftime("%Y-%m-%d"),
                "Entity": "Sistema",
            }

            resp_json = await _post("/daily", payload)
            items = resp_json.get("Items") or []
            print(f"🧠 Datos XM recibidos: {len(items)} items")

            for item in reversed(items):
                if "DailyEntities" in item:
                    for ent in item["DailyEntities"]:
                        v = ent.get("Value")
                        if v is not None:
                            valor = float(v)
                            print(f"✅ Valor encontrado ({end_d}): {valor}")
                            break
                if valor is not None:
                    break

            if valor is None:
                dias_retroceso += 1
                print(f"⚠️ Sin datos válidos en este rango, retrocediendo un día...")

        if valor is None:
            raise RuntimeError("No se pudo extraer valor del Precio Bolsa desde XM en los últimos 5 días")

        # 💡 Si llegó aquí, significa que se obtuvo correctamente desde XM
        return float(valor), "XM"

    except Exception as e:
        print(f"❌ Error al obtener PBND desde XM: {e}")
        print("🔁 Usando valor de respaldo desde configuración local...")
        cfg = cargar_configuracion()
        valor_respaldo = float(cfg.get("tarifas", {}).get("generacion", {}).get("valor_kWh", 320.5))
        return valor_respaldo, "Respaldo local (config.json)"
