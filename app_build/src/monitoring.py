import os
import json
import logging
from logging.handlers import RotatingFileHandler
import threading
from contextlib import contextmanager
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
METRICS_FILE = os.path.join(BASE_DIR, "data", "metrics.json")

# Créer les dossiers
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)

# Configuration du logging structuré
logger = logging.getLogger("BookLensLogger")
logger.setLevel(logging.INFO)
# Éviter d'ajouter plusieurs handlers si ré-importé
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=500*1024, backupCount=2, encoding="utf-8")
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "data": %(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

_metrics_lock = threading.Lock()

def _load_metrics() -> dict:
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"apis": {}}

def _save_metrics(metrics: dict):
    try:
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def track_call(api_name: str, latency: float, success: bool, error_message: str = None):
    """Enregistre un appel API dans les métriques et écrit un log JSON structuré."""
    # 1. Logging structuré JSON
    log_payload = {
        "api": api_name,
        "success": success,
        "latency_sec": round(latency, 3)
    }
    if error_message:
        log_payload["error"] = error_message
    
    # Message logué sous forme de chaîne JSON
    logger.info(json.dumps(log_payload, ensure_ascii=False))
    
    # 2. Mise à jour des métriques
    with _metrics_lock:
        metrics = _load_metrics()
        apis = metrics.setdefault("apis", {})
        api_data = apis.setdefault(api_name, {
            "calls": 0,
            "success": 0,
            "errors": 0,
            "total_latency": 0.0,
            "avg_latency": 0.0
        })
        
        api_data["calls"] += 1
        if success:
            api_data["success"] += 1
        else:
            api_data["errors"] += 1
            
        api_data["total_latency"] += latency
        api_data["avg_latency"] = round(api_data["total_latency"] / api_data["calls"], 3)
        
        _save_metrics(metrics)

@contextmanager
def track_api_call(api_name: str):
    """Context manager pour mesurer automatiquement la latence et loguer le résultat."""
    start_time = time.time()
    success = True
    error_msg = None
    try:
        yield
    except Exception as e:
        success = False
        error_msg = str(e)
        raise
    finally:
        latency = time.time() - start_time
        track_call(api_name, latency, success, error_msg)

def get_metrics() -> dict:
    """Retourne les métriques stockées."""
    with _metrics_lock:
        return _load_metrics()

def clear_metrics():
    """Réinitialise les métriques."""
    with _metrics_lock:
        _save_metrics({"apis": {}})

def get_recent_logs(limit: int = 15) -> list:
    """Retourne les dernières lignes de log sous forme de texte brut pour l'affichage."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip() for line in lines[-limit:]]
    except Exception:
        return []
