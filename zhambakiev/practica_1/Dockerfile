FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN useradd -m -u 1000 counter && \
    chown -R counter:counter /app

USER counter

EXPOSE 8000

CMD ["python", "app.py"]
