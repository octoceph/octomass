"""
Serial sensors (UART/USB) helper.

Простой пример чтения из serial-порта с использованием pyserial.
"""
import serial
from loguru import logger

def read_serial(device: str, baudrate: int = 9600, timeout: float = 1.0):
    """Откроем последовательный порт, прочитаем доступные данные и вернем строку."""
    try:
        with serial.Serial(device, baudrate=baudrate, timeout=timeout) as ser:
            data = ser.read(1024)
            return data.decode(errors='ignore')
    except Exception as e:
        logger.error("Serial read error: {}", e)
        return None
