from core.calculadora import cargar_configuracion

def calcular_componente_G(compras):
    config = cargar_configuracion()
    metodo = config["componente_G"]["metodo"]

    if metodo != "promedio_ponderado":
        raise ValueError("Método de cálculo no soportado: " + metodo)

    energia_total = sum(c.energia_kWh for c in compras)
    if energia_total == 0:
        return 0.0
    costo_total = sum(c.energia_kWh * c.precio_kWh for c in compras)
    return round(costo_total / energia_total, 2)
