from core.calculadora import cargar_configuracion
from servicios.comercializacion.modelo import DatosComercializacion, ResultadoComercializacion

# Valores base de comercialización (COP/kWh) de ejemplo
CU_C = {
    "NT1": 35.0,
    "NT2": 30.0,
    "NT3": 25.0,
    "NT4": 20.0,
    "NT5": 15.0,
}

def calcular_comercializacion(datos: DatosComercializacion) -> ResultadoComercializacion:
    nivel = datos.nivel_tension.upper()
    if nivel not in CU_C:
        raise ValueError(f"Nivel de tensión no reconocido: {nivel}")

    cu = CU_C[nivel]
    valor = datos.consumo * cu

    detalle = {
        "consumo_kwh": datos.consumo,
        "cargo_unitario_cop_kwh": cu,
        "nivel_tension": nivel,
        "zona": datos.zona,
        "formula": f"C = consumo_kwh * CU_C({nivel})"
    }

    return ResultadoComercializacion(valor=round(valor, 2), detalle=detalle)
