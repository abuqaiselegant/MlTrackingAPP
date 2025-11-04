"""
ML Experiment Tracker - Easy Integration
=========================================

Just copy this file to your project and you're ready to track experiments!

How to use:
    from mltracker import tracker
    
    # Start tracking
    tracker.start("My Cool Model", lr=0.001, epochs=100)
    
    # Log metrics while training
    for epoch in range(100):
        loss = train_step()  # your training code
        tracker.log("loss", loss, step=epoch)
    
    # Done!
    tracker.finish()
    
That's it! Check http://localhost:3000 to see your results.
"""

import requests
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class SimpleMLTracker:
    """Super easy ML experiment tracker - just 4 methods you need"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.experiment_id = None
        self.experiment_name = None
        
    def start(self, name: str, tags: Optional[List[str]] = None, **hyperparameters):
        """
        Start tracking your experiment
        
        Give it a name and add any hyperparameters you want:
        
            tracker.start("My Model", 
                         tags=['pytorch'],
                         learning_rate=0.001,
                         batch_size=32)
        """
        try:
            response = requests.post(
                f"{self.api_url}/experiments",
                json={
                    "name": name,
                    "hyperparameters": hyperparameters,
                    "tags": tags or []
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self.experiment_id = data["id"]
            self.experiment_name = name
            
            print(f"✅ Started experiment: {name}")
            print(f"   ID: {self.experiment_id}")
            print(f"   View at: http://localhost:3000/experiments/{self.experiment_id}")
            return self.experiment_id
            
        except Exception as e:
            print(f"❌ Failed to start experiment: {e}")
            raise
    
    def log(self, metric_name: str, value: float, step: Optional[int] = None):
        """
        Log a metric (like accuracy or loss)
        
        Use it like: tracker.log("accuracy", 0.95, step=10)
        """
        if not self.experiment_id:
            raise ValueError("No active experiment. Call start() first!")
        
        try:
            response = requests.post(
                f"{self.api_url}/experiments/{self.experiment_id}/metrics",
                json={
                    "metric_name": metric_name,
                    "value": float(value),
                    "step": step
                }
            )
            response.raise_for_status()
            
            step_str = f" @ step {step}" if step is not None else ""
            print(f"📊 {metric_name} = {value:.4f}{step_str}")
            
        except Exception as e:
            print(f"⚠️  Failed to log metric: {e}")
    
    def log_many(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log multiple metrics at once
        
        Easier than calling log() multiple times:
        
            tracker.log_many({
                'train_loss': 0.5,
                'val_loss': 0.6,
                'accuracy': 0.85
            }, step=10)
        """
        for name, value in metrics.items():
            self.log(name, value, step)
    
    def save_model(self, file_path: str, artifact_type: str = "model"):
        """
        Upload your model file (or any file)
        
        Examples:
            tracker.save_model("model.pkl")
            tracker.save_model("plot.png", artifact_type="visualization")
        """
        if not self.experiment_id:
            raise ValueError("No active experiment. Call start() first!")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'artifact_type': artifact_type}
                response = requests.post(
                    f"{self.api_url}/experiments/{self.experiment_id}/artifacts",
                    files=files,
                    data=data
                )
            response.raise_for_status()
            print(f"📦 Uploaded: {file_path}")
            
        except Exception as e:
            print(f"⚠️  Failed to upload file: {e}")
    
    def finish(self, status: str = "completed"):
        """
        Mark your experiment as done
        
        Use: tracker.finish() when training completes
        Or:  tracker.finish("failed") if something went wrong
        """
        if not self.experiment_id:
            print("⚠️  No active experiment to finish")
            return
        
        try:
            response = requests.put(
                f"{self.api_url}/experiments/{self.experiment_id}/status",
                json={"status": status}
            )
            response.raise_for_status()
            
            print(f"✨ Experiment '{self.experiment_name}' marked as {status}")
            print(f"   View results: http://localhost:3000/experiments/{self.experiment_id}")
            
            # Reset
            self.experiment_id = None
            self.experiment_name = None
            
        except Exception as e:
            print(f"⚠️  Failed to update status: {e}")
    
    def add_tags(self, *tags: str):
        """
        Add tags to your experiment
        
        Use: tracker.add_tags("production", "best-model")
        """
        if not self.experiment_id:
            raise ValueError("No active experiment. Call start() first!")
        
        try:
            # Get current experiment
            response = requests.get(f"{self.api_url}/experiments/{self.experiment_id}")
            response.raise_for_status()
            current_tags = response.json().get("tags", [])
            
            # Add new tags
            new_tags = list(set(current_tags + list(tags)))
            
            # Update
            response = requests.put(
                f"{self.api_url}/experiments/{self.experiment_id}/tags",
                json={"tags": new_tags}
            )
            response.raise_for_status()
            print(f"🏷️  Added tags: {', '.join(tags)}")
            
        except Exception as e:
            print(f"⚠️  Failed to add tags: {e}")


# Create a global singleton instance for easy use
tracker = SimpleMLTracker()


# Decorator for automatic experiment tracking
def track_experiment(name: str = None, **default_hyperparams):
    """
    Decorator to automatically track a training function
    
    Example:
        @track_experiment(name="My Training", epochs=100)
        def train_model(learning_rate=0.001):
            for epoch in range(100):
                loss = train_step()
                tracker.log("loss", loss, step=epoch)
            return model
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            exp_name = name or func.__name__
            
            # Merge hyperparameters
            hyperparams = {**default_hyperparams, **kwargs}
            
            # Start tracking
            tracker.start(exp_name, **hyperparams)
            
            try:
                # Run the function
                result = func(*args, **kwargs)
                tracker.finish("completed")
                return result
            except Exception as e:
                tracker.finish("failed")
                raise e
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("ML Tracker - Example Usage")
    print("=" * 60)
    
    # Start an experiment
    tracker.start(
        "Example Training Run",
        tags=["example", "test"],
        learning_rate=0.001,
        batch_size=32,
        optimizer="adam"
    )
    
    # Simulate training loop
    for epoch in range(5):
        # Simulate metrics
        train_loss = 1.0 - (epoch * 0.15)
        val_loss = 1.1 - (epoch * 0.14)
        accuracy = 0.6 + (epoch * 0.07)
        
        # Log metrics
        tracker.log_many({
            'train_loss': train_loss,
            'val_loss': val_loss,
            'accuracy': accuracy
        }, step=epoch)
    
    # Add tags
    tracker.add_tags("promising", "v2")
    
    # Finish
    tracker.finish()
    
    print("\n✅ Example completed! Check the web interface.")
