# Imagen base oficial de Python
FROM python:3.11-slim

# Crea directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (variable dinámica que definiremos en compose)
EXPOSE ${PORT}

# Comando por defecto (puerto y módulo se pasan por variables)
CMD ["sh", "-c", "uvicorn ${MODULE}:app --host 0.0.0.0 --port ${PORT} --reload"]
