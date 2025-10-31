from core.calculadora import cargar_configuracion
from servicios.perdidas_reconocidas.modelo import DatosEntrada, ResultadoPR

# Tabla de cargos unitarios (COP/kWh) — ejemplo base, ajusta con CREG 119/2007 o resoluciones vigentes
CU_PR = {
    "NT1": 45.2,
    "NT2": 38.7,
    "NT3": 29.5,
    "NT4": 18.4,
    "NT5": 12.1,
}

def calcular_pr(datos: DatosEntrada) -> ResultadoPR:
    nivel = datos.nivel_tension.upper()
    if nivel not in CU_PR:
        raise ValueError(f"Nivel de tensión no reconocido: {nivel}")

    cu = CU_PR[nivel]
    valor = datos.consumo * cu

    detalle = {
        "consumo_kwh": datos.consumo,
        "cargo_unitario_cop_kwh": cu,
        "nivel_tension": nivel,
        "zona": datos.zona,
        "formula": "PR = consumo_kwh * CU_PR(nivel_tension)"
    }

    return ResultadoPR(valor=round(valor, 2), detalle=detalle)
