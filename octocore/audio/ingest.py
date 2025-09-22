"""Pipeline integration: process audio file, extract features and optionally upload to IPFS."""
from pathlib import Path
from .dsp import load_audio, compute_melspec, compute_mfcc, detect_events_energy, simple_bird_bee_detector
from ..storage.ipfs_client import IPFSClient
from loguru import logger
import json

UPLOAD_DIR = Path("/tmp/octocore_audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def process_and_store_audio(file_path: str, metadata: dict, ipfs_client: IPFSClient = None) -> dict:
    """Полный pipeline обработки аудио-файла."""
    y, sr = load_audio(file_path)
    melspec = compute_melspec(y, sr)
    mfcc = compute_mfcc(y, sr)
    events = detect_events_energy(y, sr)
    heur = simple_bird_bee_detector(melspec)

    res = {
        "file": file_path,
        "metadata": metadata,
        "sr": int(sr),
        "melspec_shape": melspec.shape,
        "mfcc_shape": mfcc.shape,
        "events": events,
        "heuristics": heur
    }

    out_json = file_path + ".analysis.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    if ipfs_client:
        try:
            cid = ipfs_client.add_file(file_path)
            res["cid"] = cid
        except Exception as e:
            logger.error("IPFS add failed: %s", e)
            res["cid_error"] = str(e)

    logger.info("Audio processed: %s", file_path)
    return res
