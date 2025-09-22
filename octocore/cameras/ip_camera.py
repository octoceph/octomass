"""
IP Camera helpers: RTSP snapshot, SSDP discovery stub.

Модуль даёт простые утилиты для поиска устройств в локальной сети (SSDP)
и захвата одиночного кадра из RTSP потока с помощью ffmpeg.
"""
import socket
import time
import os
from typing import Optional, List, Tuple
from loguru import logger
from ..ffmpeg_helper import snapshot_rtsp

SSDP_DISCOVER = ("239.255.255.250", 1900)
SSDP_MSEARCH = "\r\n".join([
    'M-SEARCH * HTTP/1.1',
    'HOST: 239.255.255.250:1900',
    'MAN: "ssdp:discover"',
    'MX: 2',
    'ST: ssdp:all',
    '', ''
])

def ssdp_search(timeout: int = 2) -> List[Tuple[tuple, str]]:
    """Посылаем M-SEARCH и собираем ответы от устройств UPnP/SSDP в сети.
    Возвращаем список кортежей (addr, raw_response).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(timeout)
    try:
        sock.sendto(SSDP_MSEARCH.encode('utf-8'), SSDP_DISCOVER)
    except Exception as e:
        logger.error("SSDP send error: {}", e)
        return []
    devices = []
    t0 = time.time()
    while True:
        try:
            data, addr = sock.recvfrom(65507)
            devices.append((addr, data.decode('utf-8', errors='ignore')))
        except socket.timeout:
            break
        if time.time() - t0 > timeout:
            break
    logger.info("SSDP discovered {} items", len(devices))
    return devices

def rtsp_snapshot_to_tempfile(rtsp_url: str) -> Optional[str]:
    """Сохраняет snapshot в временный файл и возвращает путь, либо None при ошибке."""
    out = os.path.join("/tmp", f"snapshot_{int(time.time())}.jpg")
    ok = snapshot_rtsp(rtsp_url, out)
    return out if ok else None
