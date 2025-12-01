FROM python:3.11-slim

WORKDIR /app

RUN pip install flask requests

COPY app.py .

ENV BOT_INTERVAL=30

EXPOSE 80

CMD ["python", "app.py"]
