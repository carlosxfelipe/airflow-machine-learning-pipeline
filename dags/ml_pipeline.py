import os
import pickle
import sqlite3
from datetime import datetime

from airflow.sdk import dag, task
import pendulum
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

# Paths
AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", os.getcwd())
MODEL_DIR = os.path.join(AIRFLOW_HOME, "models")
DB_PATH = os.path.join(AIRFLOW_HOME, "models_registry.db")

default_args = {
    "owner": "airflow",
    "start_date": pendulum.datetime(2023, 1, 1, tz="UTC"),
    "catchup": False,
}

@dag(default_args=default_args, schedule=None, tags=["ml", "university"])
def ml_pipeline():
    
    @task
    def train_model() -> str:
        """Trains a logistic regression model and saves it locally."""
        # Create models directory if it doesn't exist
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # 1. Generate synthetic dataset
        X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 2. Train model
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        
        # 3. Save model
        model_filename = f"logistic_regression_{pendulum.now().format('YYYYMMDD_HHmmss')}.pkl"
        model_path = os.path.join(MODEL_DIR, model_filename)
        
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
            
        # We save test data for evaluation in the next task
        test_data_path = os.path.join(MODEL_DIR, "test_data.pkl")
        with open(test_data_path, "wb") as f:
            pickle.dump((X_test, y_test), f)
            
        return model_path

    @task
    def evaluate_model(model_path: str) -> dict:
        """Evaluates the model and returns metrics."""
        # Load model
        with open(model_path, "rb") as f:
            model = pickle.load(f)
            
        # Load test data
        test_data_path = os.path.join(MODEL_DIR, "test_data.pkl")
        with open(test_data_path, "rb") as f:
            X_test, y_test = pickle.load(f)
            
        # Predict
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        metrics = {
            "accuracy": float(acc),
            "roc_auc": float(roc_auc)
        }
        
        print(f"Model Metrics: Accuracy={acc:.4f}, ROC AUC={roc_auc:.4f}")
        return metrics

    @task
    def select_best_model(metrics: dict, threshold: float = 0.80) -> bool:
        """Selects the best model based on accuracy."""
        accuracy = metrics.get("accuracy", 0)
        if accuracy >= threshold:
            print(f"Model selected! Accuracy ({accuracy:.4f}) is >= threshold ({threshold})")
            return True
        else:
            print(f"Model rejected. Accuracy ({accuracy:.4f}) is < threshold ({threshold})")
            return False

    @task
    def publish_model(model_path: str, metrics: dict, is_selected: bool):
        """Publishes the selected model metadata to SQLite."""
        if not is_selected:
            print("Model was not selected for publishing.")
            return "Skipped"
            
        # Create or connect to SQLite DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                model_path TEXT,
                accuracy REAL,
                roc_auc REAL,
                published_at TIMESTAMP
            )
        ''')
        
        # Insert model record
        model_name = os.path.basename(model_path)
        published_at = datetime.now()
        
        cursor.execute('''
            INSERT INTO models_registry (model_name, model_path, accuracy, roc_auc, published_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (model_name, model_path, metrics['accuracy'], metrics['roc_auc'], published_at))
        
        conn.commit()
        conn.close()
        
        print(f"Model {model_name} successfully published to {DB_PATH}.")
        return "Published"

    # Define task dependencies
    trained_model_path = train_model()
    model_metrics = evaluate_model(trained_model_path)
    is_best = select_best_model(model_metrics)
    publish_model(trained_model_path, model_metrics, is_best)

# Instantiate DAG
dag_instance = ml_pipeline()
