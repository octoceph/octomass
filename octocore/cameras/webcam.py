"""
Webcam utilities — OpenCV wrapper для работы с локальными веб-камерами.
Комментарии на русском объясняют, как использовать функции.
"""
import cv2
from typing import Optional, Iterator, List
from loguru import logger
import os

def list_cameras(max_devices: int = 6) -> List[int]:
    """Пробегаем индексы устройств и возвращаем те, которые открываются (наиболее простой метод)."""
    found = []
    for i in range(max_devices):
        # На Windows используем backend CAP_DSHOW для лучшей совместимости.
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(i)
        if cap is not None and cap.isOpened():
            found.append(i)
            cap.release()
    logger.info("Detected {} cameras", len(found))
    return found

def open_camera(device_index: int = 0, width: int = 640, height: int = 480) -> Optional[cv2.VideoCapture]:
    """Открываем камеру и настраиваем разрешение. Возвращаем объект VideoCapture или None."""
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        logger.error("Cannot open camera {}", device_index)
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def frames_from_camera(cap: cv2.VideoCapture) -> Iterator:
    """Генератор, отдаёт BGR numpy-кадры. Не забывайте закрывать cap после использования."""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()
