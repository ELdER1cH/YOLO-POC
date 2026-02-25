FROM python:3.12-slim

# OpenCV-Abhängigkeiten (headless)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setzen Sie das Config-Verzeichnis auf einen beschreibbaren Pfad
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Korrekter Modellname: yolo11n.pt (ohne "v")
RUN python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"

COPY app.py .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]