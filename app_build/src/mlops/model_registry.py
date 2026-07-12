import os
import json
import shutil
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MLOPS_DIR = os.path.join(BASE_DIR, "data", "mlops")
REGISTRY_FILE = os.path.join(MLOPS_DIR, "registry.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MLOPS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

class ModelRegistry:
    @staticmethod
    def register_model(source_pkl_path: str, model_name: str, version: int, metrics: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Enregistre un modèle entraîné sous une version spécifique."""
        target_filename = f"{model_name}_v{version}.pkl"
        target_path = os.path.join(MODELS_DIR, target_filename)
        
        # Copier le fichier pickle d'origine
        if os.path.exists(source_pkl_path):
            shutil.copy(source_pkl_path, target_path)
            
        entry = {
            "model_name": model_name,
            "version": version,
            "filename": target_filename,
            "run_id": run_id,
            "status": "candidate", # candidate, active, deprecated
            "metrics": metrics
        }
        
        registry = ModelRegistry.get_registry()
        # Mettre à jour l'entrée existante si même version/nom ou en ajouter une nouvelle
        updated = False
        for idx, item in enumerate(registry):
            if item["model_name"] == model_name and item["version"] == version:
                registry[idx] = entry
                updated = True
                break
        if not updated:
            registry.append(entry)
            
        ModelRegistry._save_registry(registry)
        return entry

    @staticmethod
    def get_registry() -> List[Dict[str, Any]]:
        """Récupère l'historique complet du registre."""
        if not os.path.exists(REGISTRY_FILE):
            return []
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_registry(registry: List[Dict[str, Any]]):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

    @staticmethod
    def promote_to_active(model_name: str, version: int) -> bool:
        """Promeut une version de modèle en production (statut active)."""
        registry = ModelRegistry.get_registry()
        target_entry = None
        
        for item in registry:
            if item["model_name"] == model_name and item["version"] == version:
                target_entry = item
                break
                
        if not target_entry:
            return False
            
        # Mettre tous les autres modèles du même nom en statut deprecated ou candidate
        for item in registry:
            if item["model_name"] == model_name:
                if item["version"] == version:
                    item["status"] = "active"
                elif item["status"] == "active":
                    item["status"] = "deprecated"
                    
        ModelRegistry._save_registry(registry)
        
        # Copier la version sélectionnée vers le nom de production générique
        version_file = os.path.join(MODELS_DIR, target_entry["filename"])
        prod_file = os.path.join(MODELS_DIR, "recommender_model.pkl")
        if os.path.exists(version_file):
            shutil.copy(version_file, prod_file)
            return True
            
        return False

    @staticmethod
    def get_active_model(model_name: str) -> Dict[str, Any]:
        """Récupère les détails du modèle de production actif."""
        registry = ModelRegistry.get_registry()
        for item in registry:
            if item["model_name"] == model_name and item["status"] == "active":
                return item
        return {}
