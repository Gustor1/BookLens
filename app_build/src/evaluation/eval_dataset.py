import os
import json
from typing import List, Dict, Any
from src.evaluation.eval_models import EvalCase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CASES_FILE = os.path.join(BASE_DIR, "data", "evaluation", "eval_cases.json")

def load_eval_cases(filepath: str = DEFAULT_CASES_FILE) -> List[EvalCase]:
    """Charge les cas d'évaluation depuis le fichier JSON."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Le fichier de cas d'évaluation n'existe pas : {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not isinstance(data, list):
        raise ValueError("Le format du fichier d'évaluation doit être une liste JSON.")
        
    cases = []
    for idx, item in enumerate(data):
        try:
            case = EvalCase.from_dict(item)
            # Validation de base des valeurs autorisées
            if case.language not in ["fr", "en", "zh"]:
                raise ValueError(f"Langue '{case.language}' non prise en charge.")
            if case.priority not in ["critical", "high", "normal"]:
                raise ValueError(f"Priorité '{case.priority}' invalide.")
            cases.append(case)
        except KeyError as e:
            raise KeyError(f"Clé manquante '{e}' dans le cas de test à l'index {idx}.")
        except Exception as e:
            raise ValueError(f"Cas de test invalide à l'index {idx} : {str(e)}")
            
    return cases


def get_filtered_cases(
    cases: List[EvalCase],
    category: str = None,
    language: str = None,
    priority: str = None,
    requires_rag: bool = None
) -> List[EvalCase]:
    """Filtre les cas d'évaluation en fonction des critères."""
    filtered = cases
    if category and category != "All":
        filtered = [c for c in filtered if c.category == category]
    if language and language != "All":
        filtered = [c for c in filtered if c.language == language]
    if priority and priority != "All":
        filtered = [c for c in filtered if c.priority == priority]
    if requires_rag is not None:
        filtered = [c for c in filtered if c.requires_rag == requires_rag]
    return filtered
