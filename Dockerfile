FROM python:3.12-slim

# OpenCV-Abhängigkeiten (headless)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Modell vorab herunterladen (baked ins Image)
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]