FROM python:3.11-slim

WORKDIR /app

COPY requerement.txt .
RUN pip install --no-cache-dir -r requerement.txt

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]