import os
import json
import csv
from typing import List, Dict, Any
from src.evaluation.eval_models import EvalResult, EvalCase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(BASE_DIR, "data", "evaluation", "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_report_stats(results: List[EvalResult]) -> Dict[str, Any]:
    """Calcule les statistiques consolidées pour la suite d'évaluation."""
    if not results:
        return {}
        
    total = len(results)
    successful = sum(1 for r in results if r.success)
    score_sum = sum(r.score for r in results)
    latency_sum = sum(r.latency_ms for r in results)
    
    fallbacks = sum(1 for r in results if r.metrics.get("is_fallback", False))
    correct_routing = sum(1 for r in results if r.metrics.get("agent_routing_accuracy", False))
    valid_citations = sum(1 for r in results if r.metrics.get("citation_metadata_validity", True))
    
    # Échecs critiques de sécurité
    security_fails = sum(1 for r in results if not r.metrics.get("security_refusal", True))
    
    return {
        "total_cases": total,
        "success_rate": round((successful / total) * 100, 1) if total > 0 else 0.0,
        "avg_score": round(score_sum / total, 1) if total > 0 else 0.0,
        "avg_latency_ms": round(latency_sum / total, 1) if total > 0 else 0.0,
        "fallback_rate": round((fallbacks / total) * 100, 1) if total > 0 else 0.0,
        "correct_routing_rate": round((correct_routing / total) * 100, 1) if total > 0 else 0.0,
        "valid_citations_rate": round((valid_citations / total) * 100, 1) if total > 0 else 0.0,
        "security_critical_failures": security_fails
    }


def export_json(results: List[EvalResult], stats: Dict[str, Any], filepath: str) -> str:
    """Exporte le rapport complet au format JSON."""
    report_data = {
        "metadata": {
            "timestamp": results[0].timestamp if results else "",
            "run_id": results[0].run_id if results else ""
        },
        "stats": stats,
        "results": [r.to_dict() for r in results]
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    return filepath


def export_csv(results: List[EvalResult], filepath: str) -> str:
    """Exporte les résultats de cas au format CSV."""
    if not results:
        return filepath
        
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Case ID", "Provider", "Routing Detected", "Latency (ms)", 
            "Success", "Score", "Reasons", "Timestamp"
        ])
        for r in results:
            writer.writerow([
                r.case_id, r.provider, r.routing_detected, round(r.latency_ms, 1),
                r.success, r.score, "; ".join(r.reasons), r.timestamp
            ])
    return filepath


def export_markdown(results: List[EvalResult], stats: Dict[str, Any], filepath: str) -> str:
    """Exporte un rapport d'évaluation formaté et lisible en Markdown."""
    if not results:
        return filepath
        
    run_id = results[0].run_id
    timestamp = results[0].timestamp
    provider = results[0].provider.upper()
    
    md = f"""# Rapport d'Évaluation de l'Assistant IA — BookLens

- **Identifiant Run** : `{run_id}`
- **Date d'exécution** : `{timestamp}`
- **Provider testé** : `{provider}`

## 📊 Métriques Consolidées

| Métrique | Valeur |
|---|---|
| **Total cas exécutés** | {stats['total_cases']} |
| **Taux de succès** | `{stats['success_rate']}%` |
| **Score moyen** | `{stats['avg_score']}/100` |
| **Latence moyenne** | `{stats['avg_latency_ms']:.1f} ms` |
| **Taux de repli (Fallback)** | `{stats['fallback_rate']}%` |
| **Précision de routage** | `{stats['correct_routing_rate']}%` |
| **Citations RAG valides** | `{stats['valid_citations_rate']}%` |
| **Échecs de sécurité critiques** | `{stats['security_critical_failures']}` |

---

## 📋 Résultats Détaillés par Cas de Test

| ID Cas | Score | Succès | Latence | Routage détecté | Raisons de l'échec / Remarques |
|---|---|---|---|---|---|
"""
    for r in results:
        success_icon = "✅ PASSED" if r.success else "❌ FAILED"
        reasons_text = "; ".join(r.reasons) if r.reasons else "Aucun problème détecté"
        md += f"| `{r.case_id}` | `{r.score}/100` | {success_icon} | {r.latency_ms:.1f} ms | `{r.routing_detected}` | {reasons_text} |\n"
        
    md += """
---
*Ce rapport a été généré automatiquement par l'AI Evaluation Lab de BookLens. Il ne contient aucune information sensible.*
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)
    return filepath


def save_evaluation_run(results: List[EvalResult]) -> tuple[str, str, str]:
    """Génère et sauvegarde les trois formats de rapports d'évaluation."""
    if not results:
        raise ValueError("Aucun résultat d'évaluation à enregistrer.")
        
    run_id = results[0].run_id
    stats = generate_report_stats(results)
    
    json_path = os.path.join(RESULTS_DIR, f"report_{run_id}.json")
    csv_path = os.path.join(RESULTS_DIR, f"report_{run_id}.csv")
    md_path = os.path.join(RESULTS_DIR, f"report_{run_id}.md")
    
    export_json(results, stats, json_path)
    export_csv(results, csv_path)
    export_markdown(results, stats, md_path)
    
    return json_path, csv_path, md_path
