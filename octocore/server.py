"""
FastAPI application — основной серверный компонент для PoC.
Содержит минимальные endpoints для приёма кадров, RTSP snapshot и pin в IPFS.

Каждый endpoint подробно прокомментирован на русском.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from .utils.logging import logger
from .storage.ipfs_client import IPFSClient
from .ffmpeg_helper import snapshot_rtsp
from uuid import uuid4
from pathlib import Path

app = FastAPI(title="OctoCore API (Videomass fork)")

# Конфигурация через переменные окружения (или .env)
INFURA_ID = os.getenv("INFURA_PROJECT_ID")
INFURA_SECRET = os.getenv("INFURA_PROJECT_SECRET")
IPFS_CLIENT = IPFSClient(infura_project_id=INFURA_ID, infura_secret=INFURA_SECRET)

# Временная локальная папка для сохранения загруженных файлов
UPLOAD_DIR = Path("/tmp/octocore_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class FrameMetadata(BaseModel):
    clientId: str
    cameraId: str
    timestamp: Optional[str] = None
    notes: Optional[str] = None

@app.post("/api/v1/frames")
async def upload_frame(file: UploadFile = File(...), metadata: str = Form(...)):
    """
    Принимает multipart/form-data:
    - file: бинарный файл (image/jpeg или png)
    - metadata: JSON в строке (см. FrameMetadata)
    Сохраняет файл во временный каталог и пытается добавить в IPFS (если настроено).
    Возвращает JSON с frameId и cid (при успехе pin).
    """
    data = None
    try:
        data = FrameMetadata.parse_raw(metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"metadata parse error: {e}")

    filename = f"{uuid4().hex}_{file.filename}"
    out_path = UPLOAD_DIR / filename
    with open(out_path, "wb") as f:
        content = await file.read()
        f.write(content)
    logger.info("Saved frame %s", out_path)

    # пытаемся добавить в IPFS (если доступен)
    cid = IPFS_CLIENT.add_file(str(out_path))
    return JSONResponse({"frameId": filename, "cid": cid, "path": str(out_path)})

@app.get("/api/v1/rtsp/snapshot")
def rtsp_snapshot(url: str):
    """
    Вызов: /api/v1/rtsp/snapshot?url=rtsp://user:pass@host/stream
    Делает snapshot через ffmpeg и возвращает JPG файл.
    """
    out = UPLOAD_DIR / f"snapshot_{uuid4().hex}.jpg"
    ok = snapshot_rtsp(url, str(out))
    if not ok:
        raise HTTPException(status_code=500, detail="snapshot failed")
    return FileResponse(str(out))

@app.post("/api/v1/pin")
async def pin_request(cid: str = Form(...)):
    """
    Простая заглушка для pin запросов: возвращаем queued.
    В продакшне здесь запускается job в очереди и track status.
    """
    return {"status": "queued", "cid": cid}
