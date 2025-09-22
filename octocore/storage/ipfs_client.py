"""
Wrapper для IPFS HTTP API.

Поддерживает клиент ipfshttpclient (если локальный daemon доступен) и fallback
через Infura HTTP API (если указаны project id/secret).
"""
import ipfshttpclient
from loguru import logger
import os
import requests
from typing import Optional

class IPFSClient:
    def __init__(self, url: Optional[str] = None, infura_project_id: Optional[str]=None, infura_secret: Optional[str]=None):
        """Инициализация клиента. Если url указан, пытаемся подключиться через ipfshttpclient.
        Иначе используем Infura (HTTP) как fallback при наличии credentials."""
        self.infura_project_id = infura_project_id
        self.infura_secret = infura_secret
        if url:
            try:
                self.client = ipfshttpclient.connect(url)
            except Exception as e:
                logger.warning("ipfshttpclient connect failed: %s", e)
                self.client = None
        else:
            try:
                self.client = ipfshttpclient.connect()  # /dns/localhost/tcp/5001/http
            except Exception as e:
                logger.warning("ipfshttpclient not available: %s", e)
                self.client = None


# tail for ipfs_client.py: actual add implementation
def _add_file_with_http_fallback(self, path: str) -> Optional[str]:
    if self.client:
        res = self.client.add(path)
        # ipfshttpclient может вернуть dict или list, учитываем оба варианта
        cid = res['Hash'] if isinstance(res, dict) else res[-1]['Hash']
        logger.info("Added to ipfs: %s", cid)
        return cid
    # fallback to Infura (if credentials exist)
    if self.infura_project_id:
        url = "https://ipfs.infura.io:5001/api/v0/add"
        files = {'file': open(path, 'rb')}
        resp = requests.post(url, auth=(self.infura_project_id, self.infura_secret), files=files)
        if resp.ok:
            return resp.json()['Hash']
    logger.error("No ipfs client available")
    return None
