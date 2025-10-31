# Hereda de la imagen base
FROM tarifa-electrica-base:latest

# Copia el servicio específico
COPY ./servicios/generacion /app

# Expone el puerto
EXPOSE 8001

# Comando para ejecutar el microservicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
