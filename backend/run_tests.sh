#!/bin/bash
# Quick test runner script

echo "🧪 Running FIBO Studio Test Suite"
echo "=================================="
echo ""

cd "$(dirname "$0")"

echo "📋 Test Summary:"
echo ""

# Run tests with summary
pytest tests/ -v --tb=short --co -q 2>&1 | head -30

echo ""
echo "🚀 Running Key Tests..."
echo ""

# Run critical tests
pytest tests/test_api_endpoints.py::TestHealthEndpoints \
       tests/test_bria_client.py::TestImageGeneration::test_generate_image_async \
       tests/test_bria_client.py::TestVideoGeneration::test_generate_video_endpoint \
       tests/test_bria_client.py::TestPromptBuilding::test_build_fibo_prompt \
       -v 2>&1

echo ""
echo "✅ Test suite complete!"
echo ""
echo "For full test run: pytest tests/ -v"





