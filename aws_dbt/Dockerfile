FROM PYTHON:3.8-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

copy src/* .
CMD ["python","./producer.py"]
