# Usar una imagen base de Python 3.10 (puedes elegir una versión más reciente si lo prefieres)
FROM python:3.10

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN python -m pip install --upgrade pip
RUN pip install --force-reinstall setuptools==65.5.0 wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de tu proyecto al contenedor
COPY . .

# Exponer el puerto (si el contenedor necesita estar accesible desde fuera)
# EXPOSE 8080 # Si fuera necesario

# Ejecutar el script Python cuando el contenedor se inicie
CMD ["python", "client.py"]
