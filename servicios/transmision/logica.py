from core.calculadora import cargar_configuracion

def obtener_valor_transmision():
    config = cargar_configuracion()
    valor = config["componente_T"]["valor_fijo_transmision"]
    return round(valor, 2)
