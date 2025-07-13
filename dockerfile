FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --force-reinstall setuptools==65.5.0 wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/client.py"]
