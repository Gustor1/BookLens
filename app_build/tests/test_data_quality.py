import pytest
import os
import json
from src.data_quality import DataQualityEngine

def test_data_quality_diagnostics():
    report = DataQualityEngine.run_diagnostics()
    assert "timestamp" in report
    assert "datasets" in report
    
    # Doit contenir les datasets de base du projet
    datasets = report["datasets"]
    assert "books" in datasets or "users" in datasets or "ratings" in datasets
    
    # Vérifier que le format d'analyse de base est respecté
    for name, details in datasets.items():
        if "error" not in details:
            assert "total_rows" in details
            assert "duplicates" in details
            assert "missing_values" in details
            assert "status" in details


def test_markdown_report_generation():
    md = DataQualityEngine.generate_markdown_report()
    assert "# 🏛️ Rapport de Gouvernance & Qualité des Données" in md
    assert "Dataset" in md
