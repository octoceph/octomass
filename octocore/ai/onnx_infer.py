"""
ONNX runtime helper.

Запуск модели ONNX на CPU/GPU (провайдеры зависят от установки onnxruntime).
"""
import onnxruntime as ort
import numpy as np
from loguru import logger
from typing import Any

def run_onnx_model(model_path: str, input_array: np.ndarray, input_name: str = None):
    sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    input_name = input_name or sess.get_inputs()[0].name
    out = sess.run(None, {input_name: input_array})
    logger.debug("ONNX output shapes: %s", [o.shape for o in out])
    return out
