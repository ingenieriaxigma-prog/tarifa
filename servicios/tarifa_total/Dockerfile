FROM tarifa-electrica-base

WORKDIR /app
COPY ./servicios/tarifa_total /app

EXPOSE 8007
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
