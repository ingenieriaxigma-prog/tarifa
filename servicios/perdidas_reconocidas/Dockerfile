FROM tarifa-electrica-base:latest
COPY ./servicios/perdidas_reconocidas /app
EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
