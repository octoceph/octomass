# OctoCore — fork of Videomass (alpha) with Audio DSP

Этот репозиторий — форк проекта **Videomass**, расширённый для задач OctoCore:
мультикамерного захвата, локальной и облачной ИИ-аналитики, интеграции с IPFS/Helia/Filecoin,
поддержки сенсоров (MQTT/Modbus/Serial) и — дополнительно — полноценного аудио-движка (DSP + ML).

> ВНИМАНИЕ: это рабочий прототип («skeleton») — предназначен для локальной разработки и PoC.
> Лицензия: GPL-3.0-or-later (как у оригинального Videomass).

## Что включено в этот форк
- FastAPI сервер с эндпойнтами для приёма кадров, snapshot RTSP, загрузки и анализа аудио.
- Модули для работы с веб-камерами (OpenCV) и IP-камерами (ffmpeg snapshot).
- Audio engine: DSP (librosa), эвристики, hooks для TF/PyTorch/ONNX inference.
- Простая интеграция с IPFS (ipfshttpclient / Infura fallback) и Filecoin shim.
- Сенсоры: MQTT, Modbus, Serial (каркас).
- Dockerfile и docker-compose для локального запуска.

## Быстрый старт (локально)
1. Скопируйте `.env.example` в `.env` и заполните переменные (INFURA_PROJECT_ID и т.д.), если планируете использовать IPFS/Powergate.
2. Установите зависимости (рекомендуется poetry):
   ```bash
   poetry install
   ```
   Или pip:
   ```bash
   pip install -e .
   ```
3. Запустите сервер разработки:
   ```bash
   uvicorn octocore.server:app --reload --port 8000
   ```
4. Тестовые вызовы:
   * Snapshot RTSP:
     ```
     GET http://localhost:8000/api/v1/rtsp/snapshot?url=rtsp://user:pass@host/stream
     ```
   * Upload frame:
     ```
     POST /api/v1/frames (multipart: file, metadata)
     ```
   * Upload audio and analyze:
     ```
     POST /api/v1/audio (multipart: file, metadata)  # returns analysis (or queued)
     ```

## Audio engine (DSP + ML)
Папка `src/octocore/audio/` содержит модули:
- `dsp.py` — загрузка аудио, melspec, mfcc, spectrogram, детекция событий по энергии.
- `ml_models.py` — адаптеры для TF/Torch/ONNX моделирования.
- `ingest.py` — pipeline обработки аудио, сохранение результатов и опциональный upload в IPFS.

Примеры использования в `server.py` — endpoint `/api/v1/audio`.
