FROM tarifa-electrica-base

WORKDIR /app
COPY ./servicios/distribucion /app

EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
