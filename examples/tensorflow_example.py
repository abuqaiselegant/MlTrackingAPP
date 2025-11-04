"""
TensorFlow/Keras Integration Example
====================================

Simple example showing how to integrate ML Tracker with TensorFlow/Keras.
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np

# Import the tracker (copy mltracker.py to your project first)
from mltracker import tracker


def train_keras_model():
    """Example Keras training with ML Tracker"""
    
    # Hyperparameters
    learning_rate = 0.001
    batch_size = 32
    epochs = 10
    
    # 🚀 START TRACKING
    tracker.start(
        "Keras Neural Network",
        tags=["tensorflow", "keras", "classification"],
        learning_rate=learning_rate,
        batch_size=batch_size,
        epochs=epochs,
        optimizer="adam"
    )
    
    # Create dummy dataset
    X_train = np.random.randn(1000, 20)
    y_train = np.random.randint(0, 2, 1000)
    X_val = np.random.randn(200, 20)
    y_val = np.random.randint(0, 2, 200)
    
    # Build model
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(20,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Training loop with manual logging
    for epoch in range(epochs):
        history = model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=1,
            validation_data=(X_val, y_val),
            verbose=0
        )
        
        # 📊 LOG METRICS
        tracker.log_many({
            'train_loss': history.history['loss'][0],
            'train_accuracy': history.history['accuracy'][0],
            'val_loss': history.history['val_loss'][0],
            'val_accuracy': history.history['val_accuracy'][0]
        }, step=epoch)
        
        print(f"Epoch {epoch + 1}/{epochs}")
        print(f"  Loss: {history.history['loss'][0]:.4f}")
        print(f"  Val Loss: {history.history['val_loss'][0]:.4f}")
    
    # Save model
    model.save('keras_model.h5')
    
    # 📦 UPLOAD MODEL
    tracker.save_model('keras_model.h5')
    
    # ✨ FINISH TRACKING
    tracker.finish()


if __name__ == "__main__":
    train_keras_model()
