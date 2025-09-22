"""Adapters for ML models: TensorFlow, PyTorch, ONNX for audio inference.

Здесь приведены функции загрузки и вызова моделей.
В реальном проекте модели предзагружаются и кешируются.
"""
from typing import Any, Dict
import numpy as np
from loguru import logger

def load_tf_model(path: str):
    try:
        import tensorflow as tf
    except Exception as e:
        logger.error("TensorFlow not available: %s", e)
        raise
    model = tf.keras.models.load_model(path)
    logger.info("Loaded TF model from %s", path)
    return model

def load_torch_model(path: str, device: str = "cpu"):
    try:
        import torch
    except Exception as e:
        logger.error("Torch not available: %s", e)
        raise
    model = torch.jit.load(path, map_location=device)
    model.eval()
    logger.info("Loaded TorchScript model from %s", path)
    return model

def load_onnx_model(path: str):
    try:
        import onnxruntime as ort
    except Exception as e:
        logger.error("ONNXRuntime not available: %s", e)
        raise
    sess = ort.InferenceSession(path)
    logger.info("Loaded ONNX model from %s", path)
    return sess

def predict_tf(model, features: np.ndarray) -> Dict:
    import numpy as np
    pred = model.predict(np.expand_dims(features, 0))
    return {"pred": pred.tolist()}

def predict_torch(model, features: np.ndarray, device: str = "cpu") -> Dict:
    import torch
    t = torch.from_numpy(features).unsqueeze(0).to(device)
    with torch.no_grad():
        out = model(t)
    try:
        out_np = out.cpu().numpy()
    except Exception:
        out_np = out.numpy()
    return {"pred": out_np.tolist()}

def predict_onnx(sess, features: np.ndarray) -> Dict:
    input_name = sess.get_inputs()[0].name
    out = sess.run(None, {input_name: features.astype('float32')})
    return {"pred": [o.tolist() for o in out]}
