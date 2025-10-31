FROM tarifa-electrica-base:latest
COPY ./servicios/comercializacion /app
EXPOSE 8006
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
