"""
Modbus sensor helper.

Чтение coil/holding registers — простой пример для Modbus TCP устройств.
"""
from pymodbus.client.sync import ModbusTcpClient
from loguru import logger

def read_coils(host: str, port: int = 502, unit: int = 1, address: int = 0, count: int = 10):
    """Читать coils из устройства Modbus TCP. Возвращает list/None."""
    client = ModbusTcpClient(host, port=port)
    if not client.connect():
        logger.error("Modbus connect failed to {}:{}", host, port)
        return None
    rr = client.read_coils(address, count, unit=unit)
    client.close()
    if rr.isError():
        logger.error("Modbus read error: {}", rr)
        return None
    return rr.bits
