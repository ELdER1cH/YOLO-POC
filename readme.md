# Health-Check
curl http://localhost:8000/health

# JSON-Detections
curl -X POST http://localhost:8000/detect \
  -F "file=@./test/testbild.jpg"

# Annotiertes Bild speichern
curl -X POST http://localhost:8000/detect/image \
  -F "file=@./test/testbild.jpg" \
  -o ergebnis.jpg

# Swagger-UI
# → http://localhost:8000/docs