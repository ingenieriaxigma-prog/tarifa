def calcular_distribucion(datos):
    # Ejemplo: lógica simplificada basada en estrato y zona
    if datos.estrato in [1, 2]:
        tarifa = 100  # subsidio
    elif datos.estrato == 3:
        tarifa = 150
    else:
        tarifa = 250  # contribución

    if datos.zona == "rural":
        tarifa *= 0.9  # posible ajuste por zona

    return round(tarifa * datos.consumo_kWh, 2)
