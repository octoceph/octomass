"""
Filecoin orchestration shim.

Примеры вызовов для Powergate/Estuary. В продакшне нужна state-machine и handling ошибок,
retry-логика и webhook-обработчики событий.
"""
import httpx
from loguru import logger
from typing import List, Dict, Any

class FilecoinOrchestrator:
    def __init__(self, powergate_url: str, api_token: str = None):
        self.base = powergate_url.rstrip('/')
        self.token = api_token
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def push_cids(self, cids: List[str], policy: Dict[str, Any]) -> Dict[str, Any]:
        """Инициирует оркестрацию сделки в Powergate / Estuary. Возвращает ответ сервиса."""
        body = {"cids": cids, "policy": policy}
        url = f"{self.base}/api/v0/deals"
        resp = httpx.post(url, json=body, headers=self.headers, timeout=60.0)
        if resp.status_code != 200:
            logger.error("Powergate error: %s", resp.text)
            raise RuntimeError(resp.text)
        return resp.json()
