import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from ultralytics import YOLO
from PIL import Image

app = FastAPI(title="YOLOv8 Inference API")

# Modell einmalig laden (beim Start)
model = YOLO("yolo11n.pt")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
async def detect(
    file: UploadFile = File(...),
    conf: float = 0.25,
):
    """Objekterkennung auf hochgeladenem Bild. Gibt JSON mit Detections zurück."""
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    results = model.predict(source=image, conf=conf, verbose=False)
    detections = []

    for r in results:
        for box in r.boxes:
            detections.append({
                "class": r.names[int(box.cls)],
                "confidence": round(float(box.conf), 4),
                "bbox": [round(float(c), 2) for c in box.xyxy[0].tolist()],
            })

    return JSONResponse(content={"detections": detections, "count": len(detections)})


@app.post("/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    conf: float = 0.25,
):
    """Gibt das annotierte Bild (mit Bounding-Boxes) als JPEG zurück."""
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    results = model.predict(source=image, conf=conf, verbose=False)
    annotated = results[0].plot()  # numpy array (BGR)

    # BGR → RGB → JPEG
    img_rgb = Image.fromarray(annotated[..., ::-1])
    buf = io.BytesIO()
    img_rgb.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")