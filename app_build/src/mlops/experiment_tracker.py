import os
import json
import datetime
import hashlib
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MLOPS_DIR = os.path.join(BASE_DIR, "data", "mlops")
RUNS_FILE = os.path.join(MLOPS_DIR, "runs.json")

os.makedirs(MLOPS_DIR, exist_ok=True)

class ExperimentTracker:
    @staticmethod
    def compute_dataset_hash(df) -> str:
        """Calcule un hash MD5 du dataset pour le versionner."""
        try:
            # Hash basé sur les dimensions et les valeurs clés pour être rapide et fiable
            summary = f"{df.shape[0]}_{df.shape[1]}_{df.head(10).to_string()}"
            return hashlib.md5(summary.encode("utf-8")).hexdigest()[:8]
        except Exception:
            return "unknown_hash"

    @staticmethod
    def log_run(model_name: str, params: Dict[str, Any], metrics: Dict[str, Any], dataset_size: int, dataset_hash: str) -> Dict[str, Any]:
        """Enregistre un run d'entraînement localement."""
        run_data = {
            "run_id": hashlib.md5(f"{model_name}_{datetime.datetime.now().isoformat()}".encode("utf-8")).hexdigest()[:8],
            "model_name": model_name,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size": dataset_size,
            "dataset_hash": dataset_hash,
            "params": params,
            "metrics": metrics
        }
        
        runs = ExperimentTracker.get_all_runs()
        runs.insert(0, run_data) # Ajouter au début
        
        # Limiter à 50 runs pour éviter la croissance infinie du fichier
        runs = runs[:50]
        
        with open(RUNS_FILE, "w", encoding="utf-8") as f:
            json.dump(runs, f, ensure_ascii=False, indent=2)
            
        return run_data

    @staticmethod
    def get_all_runs() -> List[Dict[str, Any]]:
        """Récupère l'ensemble des runs enregistrés."""
        if not os.path.exists(RUNS_FILE):
            return []
        try:
            with open(RUNS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def get_latest_run(model_name: str = None) -> Dict[str, Any]:
        """Retourne le dernier run d'entraînement (éventuellement filtré par nom de modèle)."""
        runs = ExperimentTracker.get_all_runs()
        if not runs:
            return {}
        if model_name:
            for r in runs:
                if r["model_name"] == model_name:
                    return r
            return {}
        return runs[0]
