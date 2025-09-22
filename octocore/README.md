# OctoCore — fork of Videomass (alpha)

Этот репозиторий — форк проекта **Videomass**, расширённый для задач OctoCore:
мультикамерного захвата, локальной и облачной ИИ-аналитики, интеграции с IPFS/Helia/Filecoin,
а также поддержки сенсоров (MQTT/Modbus/Serial) и прокси для IP-камер.

> ВНИМАНИЕ: это рабочий прототип («skeleton») — предназначен для локальной разработки и PoC.
> Лицензия: GPL-3.0-or-later (как у оригинального Videomass). 

## Что включено в этот форк
- FastAPI сервер с эндпойнтами для приёма кадров, snapshot RTSP и pin в IPFS.
- Модули для работы с веб-камерами (OpenCV) и IP-камерами (ffmpeg snapshot).
- Простая интеграция с IPFS (ipfshttpclient / Infura fallback).
- Шим для Filecoin (Powergate/Estuary) — пример вызова.
- Сенсоры: MQTT, Modbus, Serial (каркас).
- Utility: ffmpeg helper, onnx runtime helper.
- Docker compose для быстрого локального запуска.

## Быстрый старт (локально)
1. Скопируйте `.env.example` в `.env` и заполните переменные (INFURA_PROJECT_ID и т.д.), если планируете использовать IPFS/Powergate.
2. Установите зависимости:
   * Рекомендуется использовать `poetry`:
     ```bash
     poetry install
     ```
   * Или стандартный pip:
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

## Архитектура (кратко)
Проект делится на модули:
- `cameras/` — webcam, ip_camera, discovery
- `sensors/` — mqtt_sensor, modbus_sensor, serial_sensor
- `storage/` — ipfs_client, filecoin shim
- `ai/` — примеры onnx inference, mobilenet demo
- `server.py` — FastAPI точки входа для ingest/pin/archive

Подробная архитектура и ADR находятся в репозитории (ADR был сгенерирован отдельно).

## Цели форка и стратегия сообщества
- Поддерживать совместимость с пресетами Videomass.
- Давать путь миграции существующим пользователям Videomass.
- Привлечь OSS-сообщество: оформить CONTRIBUTING, хорошие первые задачи, CI.
- Модель монетизации: open-core + SaaS (Filecoin-as-a-Service, managed GPU inference).

## Дальше
- Я могу сгенерировать OpenAPI spec, CI workflow и релизный pipeline.
- Могу подготовить руководства по развёртыванию Powergate / Estuary / MinIO.
