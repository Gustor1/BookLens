import pytest
import os
import json
import shutil
import tempfile
import pandas as pd
from unittest.mock import patch
from src.mlops.experiment_tracker import ExperimentTracker
from src.mlops.model_registry import ModelRegistry
from src.mlops.drift_monitor import DriftMonitor
from src.mlops.training_service import TrainingService

TEST_DIR = tempfile.mkdtemp()

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_dirs():
    os.makedirs(TEST_DIR, exist_ok=True)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


def test_experiment_tracker():
    df_test = pd.DataFrame({
        "Book-Title": ["Book A", "Book B", "Book C"],
        "Book-Rating": [8, 9, 10]
    })
    
    dataset_hash = ExperimentTracker.compute_dataset_hash(df_test)
    assert len(dataset_hash) == 8
    
    # Simuler le chemin du fichier runs.json
    test_runs_file = os.path.join(TEST_DIR, "runs.json")
    with patch("src.mlops.experiment_tracker.RUNS_FILE", test_runs_file):
        run = ExperimentTracker.log_run(
            model_name="test_model",
            params={"alpha": 0.5},
            metrics={"coverage": 0.95},
            dataset_size=3,
            dataset_hash=dataset_hash
        )
        assert run["model_name"] == "test_model"
        assert run["metrics"]["coverage"] == 0.95
        
        runs = ExperimentTracker.get_all_runs()
        assert len(runs) == 1
        assert runs[0]["run_id"] == run["run_id"]


def test_model_registry():
    test_registry_file = os.path.join(TEST_DIR, "registry.json")
    test_models_dir = os.path.join(TEST_DIR, "models")
    os.makedirs(test_models_dir, exist_ok=True)
    
    # Créer un faux pkl source
    dummy_source = os.path.join(TEST_DIR, "dummy.pkl")
    with open(dummy_source, "w") as f:
        f.write("dummy pickle content")
        
    with patch("src.mlops.model_registry.REGISTRY_FILE", test_registry_file), \
         patch("src.mlops.model_registry.MODELS_DIR", test_models_dir):
         
        entry = ModelRegistry.register_model(
            source_pkl_path=dummy_source,
            model_name="hybrid_model",
            version=1,
            metrics={"coverage": 0.8},
            run_id="run123"
        )
        assert entry["version"] == 1
        assert entry["status"] == "candidate"
        
        # Promouvoir
        success = ModelRegistry.promote_to_active("hybrid_model", 1)
        assert success
        
        active = ModelRegistry.get_active_model("hybrid_model")
        assert active["status"] == "active"
        assert active["version"] == 1


def test_drift_monitor():
    # Dataset sain
    df_healthy = pd.DataFrame({
        "Book-Title": ["A", "B", "C"],
        "Book-Rating": [8.0, 9.0, 7.5],
        "Theme": ["Sci-Fi", "Fantasy", "Sci-Fi"]
    })
    health = DriftMonitor.analyze_dataset_health(df_healthy)
    assert health["status"] == "healthy"
    
    # Dataset avec dérive (ratings modifiés)
    df_drifted = pd.DataFrame({
        "Book-Title": ["A", "B", "C"],
        "Book-Rating": [4.0, 5.0, 3.5], # Baisse significative de la note moyenne
        "Theme": ["Fantasy", "Fantasy", "Fantasy"]
    })
    
    drift = DriftMonitor.calculate_distribution_drift(df_healthy, df_drifted)
    assert drift["rating_mean_drift"] > 3.0
    assert drift["drift_detected"]


def test_training_service():
    df_train = pd.DataFrame({
        "User-ID": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "Book-Title": ["Book A", "Book A", "Book A", "Book B", "Book B", "Book B", "Book C", "Book C", "Book C"],
        "Book-Rating": [8, 9, 7, 10, 8, 9, 7, 8, 9],
        "Book-Author": ["Author 1", "Author 1", "Author 1", "Author 2", "Author 2", "Author 2", "Author 3", "Author 3", "Author 3"]
    })
    
    test_runs_file = os.path.join(TEST_DIR, "runs_ts.json")
    test_registry_file = os.path.join(TEST_DIR, "registry_ts.json")
    test_models_dir = os.path.join(TEST_DIR, "models_ts")
    os.makedirs(test_models_dir, exist_ok=True)
    
    with patch("src.mlops.experiment_tracker.RUNS_FILE", test_runs_file), \
         patch("src.mlops.model_registry.REGISTRY_FILE", test_registry_file), \
         patch("src.mlops.model_registry.MODELS_DIR", test_models_dir):
         
         run_pop = TrainingService.train_and_register(df_train, strategy="popularity")
         assert run_pop["model_name"] == "popularity_baseline"
         
         run_content = TrainingService.train_and_register(df_train, strategy="content_based")
         assert run_content["model_name"] == "content_based_model"
