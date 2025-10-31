FROM tarifa-electrica-base

WORKDIR /app
COPY ./servicios/transmision /app

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
