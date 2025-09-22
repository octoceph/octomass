"""
Утилиты вокруг FFmpeg (ffmpeg-python) и запуск CLI команд.
Функции используются для snapshot из RTSP, транскодинга, таймлапсов и других операций.
"""
import ffmpeg
import subprocess
import shlex
from loguru import logger
from typing import Optional
import os

def snapshot_rtsp(rtsp_url: str, out_path: str, timeout: int = 10) -> bool:
    """
    Делает один кадр из RTSP потока с помощью ffmpeg:
    ffmpeg -y -i <rtsp> -frames:v 1 -q:v 2 out.jpg

    Возвращает True при успешном создании файла.
    """
    try:
        (
            ffmpeg
            .input(rtsp_url, rtsp_transport='tcp', timeout=timeout*1000000)
            .output(out_path, vframes=1, qscale=2)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info("Snapshot saved to {}", out_path)
        return True
    except ffmpeg.Error as e:
        # Выводим stderr ffmpeg в лог для диагностики.
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e)
        logger.error("FFmpeg error: {}", stderr)
        return False

def ffmpeg_run_cmd(cmd: str) -> int:
    """Запуск произвольной ffmpeg команды через shell (с разбором и логированием)."""
    logger.debug("Run command: {}", cmd)
    proc = subprocess.run(shlex.split(cmd), capture_output=True)
    if proc.returncode != 0:
        logger.error("FFmpeg failed: {}", proc.stderr.decode(errors='ignore'))
    return proc.returncode
