# Test Suite

## Running Tests

### All Tests
```bash
cd backend
pytest tests/ -v
```

### Specific Test Files
```bash
pytest tests/test_api_endpoints.py -v
pytest tests/test_bria_client.py -v
pytest tests/test_integration.py -v
```

### Specific Test Classes
```bash
pytest tests/test_api_endpoints.py::TestHealthEndpoints -v
pytest tests/test_bria_client.py::TestImageGeneration -v
```

### Live Tests (Requires API Token)
```bash
# Set BRIA_API_TOKEN in .env first
pytest tests/test_endpoints_live.py -v
```

## Test Coverage

### Unit Tests
- ✅ Health check endpoints
- ✅ Script parsing endpoints
- ✅ BRIA API client initialization
- ✅ Image generation endpoint format
- ✅ Video generation endpoint format
- ✅ FIBO prompt building
- ✅ LLM translation
- ✅ Error handling

### Integration Tests
- ✅ Full pipeline (script → storyboard)
- ✅ Endpoint integration
- ✅ BRIA endpoint format verification

### Live Tests
- ✅ API connection
- ✅ Endpoint format verification
- ⚠️  Image generation (requires model_id)

## Test Results

Run tests to verify:
1. ✅ Endpoints are correctly formatted
2. ✅ BRIA API client uses correct URLs
3. ✅ Error handling works
4. ✅ Full pipeline integration

## Fixing Test Failures

If tests fail:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify `.env` has `BRIA_API_TOKEN` set
3. Check that endpoints match your BRIA dashboard
4. Run with `-v` flag for detailed output





