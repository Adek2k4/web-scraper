FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY engine.py /app/
COPY engine/app.py /app/

EXPOSE 5001

CMD ["python", "app.py"]
