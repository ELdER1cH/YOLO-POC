## Copilot instructions — quick, actionable (short)

This repo is a minimal FastAPI service that runs Ultralytics YOLO inference on images.
Keep changes small and code-focused: most logic lives in `app.py` and the project expects a single model file provided at runtime.

- Entrypoint: `app.py` (FastAPI app object `app`).
- Model: loaded at module import in `app.py` (e.g. `model = YOLO("yolov11n.pt")`). Treat the global `model` as a singleton to be reused across requests.
- Endpoints:
  - `GET /health` — health check
  - `POST /detect` — returns JSON detections; form field `file`, optional `conf` float
  - `POST /detect/image` — returns an annotated JPEG image

Key, discoverable repo-specific facts
- Weight file location: the app expects a weight file in the repo root at import-time. There is a known mismatch: `app.py` references `yolov11n.pt` while this repo contains `yolov8n.pt`. Resolve by placing the canonical weight in the repo root or mounting it at runtime.
- Model results: `model.predict(...)` returns a list of `Results`. Code uses `results[0]`. For each `r` the detections are in `r.boxes` and each `box` exposes `box.cls`, `box.conf`, and `box.xyxy`. Class labels are found at `r.names[int(box.cls)]`.
- Annotated images: `results[0].plot()` returns a BGR numpy array. The code converts to RGB using `annotated[..., ::-1]` before saving with Pillow.
- Response shape: JSON detection objects use `{ "class": <str>, "confidence": <float>, "bbox": [x1, y1, x2, y2] }`. Keep this shape for backward compatibility when changing the API.
- Concurrency: inference is invoked synchronously inside async endpoints; this blocks the event loop. The current code runs as a simple single-process service. If you change this, add tests and performance checks (see Testing section below).

Developer workflows (practical commands)
- Install deps: `pip install -r requirements.txt`.
- Run dev server: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`.
- Docker: `docker build -t yolo-poc .` then run with weights mounted or baked into the image. `docker-compose.yml` exists for convenience and exposes port 8000.

Quick smoke-test examples (already in repo)
- JSON detections: `curl -X POST http://localhost:8000/detect -F "file=@./test/pexels-mali-102104.jpg"`
- Annotated image: `curl -X POST http://localhost:8000/detect/image -F "file=@./test/pexels-mali-102104.jpg" -o ergebnis.jpg`

Files to inspect when making changes
- `app.py` — main logic, model loading, endpoints, response shapes.
- `requirements.txt` — pinned dependencies: ultralytics, fastapi, uvicorn, pillow, python-multipart.
- `Dockerfile`, `docker-compose.yml` — container/native lib expectations (e.g. libgl and glib libs are installed in the Dockerfile).
- `test/` — sample images for local smoke tests.

Testing, benchmarks, and safety checks
- There are no unit tests in the repo. When adding functionality, include a small smoke test that posts one image to `/detect` and asserts the JSON shape.
- If you alter inference behavior (e.g. make it non-blocking or add batch processing), add a simple benchmark script that measures request latency on CPU and include instructions in the PR.

What to confirm before large changes
- Which model weights are canonical (yolov8n.pt vs yolov11n.pt) and whether weights should be in-repo or mounted at runtime.
- Whether GPU support or multi-worker concurrency is required (this affects dependencies, Dockerfile, and deployment).

If any of the above is unclear or you'd like me to add a smoke-test, CI, or switch to GPU-enabled images, tell me which area to expand and I'll update these instructions accordingly.
