FROM tarifa-electrica-base

WORKDIR /app
ENV PYTHONPATH=/app:/app/core
COPY ./servicios/comercializacion /app

EXPOSE 8006
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
