"""
PyTorch Integration Example
===========================

Simple example showing how to integrate ML Tracker with PyTorch training.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Import the tracker (copy mltracker.py to your project first)
from mltracker import tracker


# Simple neural network
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(10, 50)
        self.fc2 = nn.Linear(50, 1)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def train_pytorch_model():
    """Example PyTorch training with ML Tracker"""
    
    # Hyperparameters
    learning_rate = 0.001
    batch_size = 32
    epochs = 10
    
    # 🚀 START TRACKING
    tracker.start(
        "PyTorch Training Example",
        tags=["pytorch", "regression"],
        learning_rate=learning_rate,
        batch_size=batch_size,
        epochs=epochs,
        optimizer="adam"
    )
    
    # Create dummy dataset
    X = torch.randn(1000, 10)
    y = torch.randn(1000, 1)
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Model, loss, optimizer
    model = SimpleNet()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training loop
    for epoch in range(epochs):
        total_loss = 0
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        
        # 📊 LOG METRICS
        tracker.log("train_loss", avg_loss, step=epoch)
        
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
    
    # Save model
    torch.save(model.state_dict(), "pytorch_model.pth")
    
    # 📦 UPLOAD MODEL
    tracker.save_model("pytorch_model.pth")
    
    # ✨ FINISH TRACKING
    tracker.finish()


if __name__ == "__main__":
    train_pytorch_model()
