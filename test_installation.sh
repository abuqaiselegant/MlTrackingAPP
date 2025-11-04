#!/bin/bash

# 🚀 ML Tracker - Test Installation Script
# This script verifies that the ML Tracker is working correctly

echo "============================================"
echo "🧪 Testing ML Tracker Installation"
echo "============================================"
echo ""

# Check if backend is running
echo "1️⃣  Checking if backend is running..."
if curl -s http://localhost:8000/experiments > /dev/null 2>&1; then
    echo "   ✅ Backend is running on http://localhost:8000"
else
    echo "   ❌ Backend is NOT running!"
    echo "   👉 Start it with: docker-compose up -d"
    exit 1
fi

echo ""

# Check if frontend is accessible
echo "2️⃣  Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on http://localhost:3000"
else
    echo "   ❌ Frontend is NOT running!"
    echo "   👉 Start it with: cd frontend && npm run dev"
    exit 1
fi

echo ""

# Test creating an experiment via API
echo "3️⃣  Testing API - Creating test experiment..."
RESPONSE=$(curl -s -X POST http://localhost:8000/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Experiment",
    "hyperparameters": {"test": true},
    "tags": ["test"]
  }')

EXPERIMENT_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ ! -z "$EXPERIMENT_ID" ]; then
    echo "   ✅ Experiment created with ID: $EXPERIMENT_ID"
else
    echo "   ❌ Failed to create experiment"
    exit 1
fi

echo ""

# Test logging a metric
echo "4️⃣  Testing API - Logging metric..."
curl -s -X POST http://localhost:8000/experiments/$EXPERIMENT_ID/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "test_metric",
    "value": 0.95,
    "step": 1
  }' > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Metric logged successfully"
else
    echo "   ❌ Failed to log metric"
    exit 1
fi

echo ""

# Cleanup - Delete test experiment
echo "5️⃣  Cleaning up test experiment..."
curl -s -X DELETE http://localhost:8000/experiments/$EXPERIMENT_ID > /dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Test experiment deleted"
else
    echo "   ⚠️  Failed to delete test experiment (ID: $EXPERIMENT_ID)"
fi

echo ""
echo "============================================"
echo "✨ All tests passed! ML Tracker is ready!"
echo "============================================"
echo ""
echo "📚 Next steps:"
echo "   1. Copy mltracker.py to your ML project"
echo "   2. Add these lines to your training code:"
echo ""
echo "      from mltracker import tracker"
echo "      tracker.start('My Experiment')"
echo "      tracker.log('loss', 0.5, step=1)"
echo "      tracker.finish()"
echo ""
echo "   3. View results at http://localhost:3000"
echo ""
echo "📖 See QUICK_START.md for more examples!"
echo ""
