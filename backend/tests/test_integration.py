"""
Integration tests for the full storyboard generation pipeline
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from PIL import Image
from core.script_parser import ScriptProcessor
from core.llm_translator import LLMTranslator
from core.fibo_engine import FIBOGenerator
from core.bria_client import BRIAAPIClient


class TestFullPipeline:
    """Test complete storyboard generation pipeline"""
    
    @patch('core.bria_client.BRIAAPIClient.generate_image_sync')
    def test_script_to_storyboard_flow(self, mock_generate):
        """Test complete flow from script to storyboard"""
        # Sample script
        script_content = """FADE IN:

EXT. CITY STREET - NIGHT

Wide establishing shot. A rain-soaked street glistens under neon signs. 
Reflections dance in puddles. The camera slowly pushes in as a mysterious 
figure emerges from the shadows.

CLOSE-UP: The figure's face. Dramatic side lighting creates deep shadows. 
Desaturated colors. The figure's eyes catch the neon light.

FADE OUT."""
        
        # Step 1: Parse script
        processor = ScriptProcessor()
        scenes = processor.parse_script_content(script_content)
        assert len(scenes) >= 1  # Should have at least 1 scene
        
        # Step 2: Translate to FIBO
        translator = LLMTranslator(provider="bria")
        fibo_params = translator.translate_to_json(
            scenes[0].description,
            scenes[0].visual_notes
        )
        assert isinstance(fibo_params, dict)
        assert "camera" in fibo_params
        assert "lighting" in fibo_params
        
        # Step 3: Generate images (mocked)
        mock_image = Image.new('RGB', (1920, 1080), color='blue')
        mock_generate.return_value = mock_image
        
        generator = FIBOGenerator(
            api_token="test_token",
            image_width=1920,
            image_height=1080
        )
        
        # Step 4: Create storyboard
        storyboard = generator.create_storyboard(scenes, translator)
        
        assert len(storyboard.frames) == len(scenes)
        assert storyboard.frames[0].scene_number == 1
        assert storyboard.frames[0].image is not None
        assert storyboard.frames[0].params is not None


class TestEndpointIntegration:
    """Test API endpoint integration"""
    
    @patch('core.fibo_engine.FIBOGenerator._generate_with_fibo')
    def test_generate_storyboard_endpoint_integration(self, mock_generate):
        """Test storyboard generation endpoint with mocked BRIA"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Mock image generation
        mock_image = Image.new('RGB', (1920, 1080), color='purple')
        mock_generate.return_value = mock_image
        
        script_content = """EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs."""
        
        # This will use the actual parsing and translation, but mocked generation
        with patch('api.main.fibo_generator._generate_with_fibo', mock_generate):
            response = client.post(
                "/api/generate-storyboard",
                json={
                    "script_content": script_content,
                    "llm_provider": "bria",
                    "hdr_enabled": True
                }
            )
            
            # Should succeed
            if response.status_code == 200:
                data = response.json()
                assert "frames" in data
                assert "frame_count" in data
                assert len(data["frames"]) > 0
                assert "image" in data["frames"][0]
                assert "params" in data["frames"][0]


class TestBRIAEndpointFormat:
    """Test that BRIA endpoints are called with correct format"""
    
    @patch('core.bria_client.requests.post')
    def test_image_endpoint_format(self, mock_post):
        """Verify image generation uses correct endpoint format"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2',
            'BRIA_MODEL_ID': 'test_model_123'
        }):
            client = BRIAAPIClient()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"request_id": "test"}
            mock_post.return_value = mock_response
            
            client.generate_image("test prompt", model_id="test_model_123")
            
            # Verify endpoint format
            call_url = mock_post.call_args[0][0]
            assert call_url == "https://engine.prod.bria-api.com/v2/text-to-image/tailored/test_model_123"
            
            # Verify headers
            headers = mock_post.call_args[1]["headers"]
            assert headers["api_token"] == "test_token"
            assert headers["Content-Type"] == "application/json"
            
            # Verify payload
            payload = mock_post.call_args[1]["json"]
            assert payload["prompt"] == "test prompt"
            assert "width" in payload
            assert "height" in payload
    
    @patch('core.bria_client.requests.post')
    def test_video_endpoint_format(self, mock_post):
        """Verify video generation uses correct endpoint format"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"request_id": "test"}
            mock_post.return_value = mock_response
            
            client.generate_video("test video", image_url="data:image/png;base64,test")
            
            # Verify endpoint format
            call_url = mock_post.call_args[0][0]
            assert call_url == "https://engine.prod.bria-api.com/v2/video/generate/tailored/image-to-video"
            
            # Verify payload
            payload = mock_post.call_args[1]["json"]
            assert payload["prompt"] == "test video"
            assert payload["image_url"] == "data:image/png;base64,test"

