from core.calculadora import cargar_configuracion
from servicios.restricciones.modelo import DatosRestricciones, ResultadoRestricciones

# Valores de ejemplo (deberás reemplazarlos con los oficiales XM/CREG)
CU_R = {
    "NT1": 2.7,
    "NT2": 2.5,
    "NT3": 2.3,
    "NT4": 2.1,
    "NT5": 2.0,
}

def calcular_restricciones(datos: DatosRestricciones) -> ResultadoRestricciones:
    nivel = datos.nivel_tension.upper()
    if nivel not in CU_R:
        raise ValueError(f"Nivel de tensión no reconocido: {nivel}")

    cu = CU_R[nivel]
    valor = datos.consumo * cu

    detalle = {
        "consumo_kwh": datos.consumo,
        "cargo_unitario_cop_kwh": cu,
        "nivel_tension": nivel,
        "zona": datos.zona,
        "formula": f"R = consumo_kwh * CU_R({nivel})"
    }

    return ResultadoRestricciones(valor=round(valor, 2), detalle=detalle)
