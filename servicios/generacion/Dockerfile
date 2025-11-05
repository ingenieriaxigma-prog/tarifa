FROM tarifa-electrica-base

WORKDIR /app
ENV PYTHONPATH=/app:/app/core

# Copia los archivos del microservicio
COPY ./servicios/generacion /app

# 🔹 Copia la carpeta "config" general para acceder a normativa_config.json
COPY ./config /app/config

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

