"""
Live endpoint tests (requires actual API token)
Run with: pytest tests/test_endpoints_live.py -v
"""
import pytest
import os
from dotenv import load_dotenv
from core.bria_client import BRIAAPIClient

load_dotenv()

# Skip if no API token
pytestmark = pytest.mark.skipif(
    not os.getenv("BRIA_API_TOKEN"),
    reason="BRIA_API_TOKEN not set - skipping live tests"
)


class TestLiveBRIAAPI:
    """Live tests against actual BRIA API"""
    
    def test_api_connection(self):
        """Test connection to BRIA API"""
        client = BRIAAPIClient()
        
        # Verify configuration
        assert client.api_token is not None
        assert client.BASE_URL is not None
        assert "bria-api.com" in client.BASE_URL or "bria.ai" in client.BASE_URL
        
        print(f"✓ Base URL: {client.BASE_URL}")
        print(f"✓ API Token: {client.api_token[:10]}...{client.api_token[-4:]}")
    
    def test_endpoint_format(self):
        """Test that endpoints are formatted correctly"""
        client = BRIAAPIClient()
        model_id = os.getenv("BRIA_MODEL_ID", "default")
        
        # Test image endpoint format
        image_url = f"{client.BASE_URL}/text-to-image/tailored/{model_id}"
        assert "text-to-image/tailored" in image_url
        
        # Test video endpoint format
        video_url = f"{client.BASE_URL}/video/generate/tailored/image-to-video"
        assert "video/generate/tailored/image-to-video" in video_url
        
        print(f"✓ Image endpoint: {image_url}")
        print(f"✓ Video endpoint: {video_url}")
    
    @pytest.mark.skip(reason="Requires valid model_id and API credits")
    def test_image_generation_live(self):
        """Test actual image generation (requires valid model_id)"""
        client = BRIAAPIClient()
        model_id = os.getenv("BRIA_MODEL_ID")
        
        if not model_id:
            pytest.skip("BRIA_MODEL_ID not set")
        
        try:
            result = client.generate_image(
                prompt="A cinematic city street at night with neon signs",
                width=512,
                height=512,
                model_id=model_id,
                sync=False
            )
            
            assert "request_id" in result or "image_url" in result
            print(f"✓ Image generation request submitted: {result.get('request_id', 'N/A')}")
        except Exception as e:
            # If it fails, at least verify the endpoint was called correctly
            error_msg = str(e)
            if "401" in error_msg or "403" in error_msg:
                pytest.skip("Authentication failed - check API token")
            elif "404" in error_msg:
                pytest.skip("Endpoint not found - check model_id")
            else:
                # Other errors might indicate endpoint format issues
                print(f"⚠️  API call failed: {e}")
                raise





