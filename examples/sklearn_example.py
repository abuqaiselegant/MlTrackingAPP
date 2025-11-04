"""
Scikit-Learn Integration Example
=================================

Simple example showing how to integrate ML Tracker with scikit-learn.
"""

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle

# Import the tracker (copy mltracker.py to your project first)
from mltracker import tracker


def train_sklearn_model():
    """Example scikit-learn training with ML Tracker"""
    
    # Hyperparameters
    n_estimators = 100
    max_depth = 10
    random_state = 42
    
    # 🚀 START TRACKING
    tracker.start(
        "Random Forest Classification",
        tags=["sklearn", "random-forest", "classification"],
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    
    # Create dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        random_state=random_state
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # 📊 LOG METRICS
    tracker.log_many({
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    })
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Save model
    with open('sklearn_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # 📦 UPLOAD MODEL
    tracker.save_model('sklearn_model.pkl')
    
    # ✨ FINISH TRACKING
    tracker.finish()


if __name__ == "__main__":
    train_sklearn_model()
