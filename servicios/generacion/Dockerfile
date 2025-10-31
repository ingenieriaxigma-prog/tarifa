FROM tarifa-electrica-base

WORKDIR /app

# Copia el código fuente del microservicio
COPY ./servicios/generacion /app

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

