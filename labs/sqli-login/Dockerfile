FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY app.py .
COPY init_db.py .

# Initialize database on build
RUN python init_db.py

EXPOSE 80

CMD ["python", "app.py"]
