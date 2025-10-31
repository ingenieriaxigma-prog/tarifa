FROM tarifa-electrica-base

WORKDIR /app
COPY ./servicios/restricciones /app

EXPOSE 8005
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
