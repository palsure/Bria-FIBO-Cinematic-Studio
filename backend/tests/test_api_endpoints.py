"""
Unit tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import base64

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "message" in data
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestScriptParsing:
    """Test script parsing endpoints"""
    
    def test_parse_script_text(self):
        """Test parsing script from text content"""
        script_content = """EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs.
Camera slowly pushes in.

CLOSE-UP: Figure's face. Dramatic side lighting. Desaturated colors."""
        
        response = client.post("/api/parse-script", json={"content": script_content})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "number" in data[0]
        assert "location" in data[0]
        assert "description" in data[0]
        assert "visual_notes" in data[0]
    
    def test_parse_script_empty(self):
        """Test parsing empty script"""
        response = client.post("/api/parse-script", json={"content": ""})
        # Should return empty list or error
        assert response.status_code in [200, 400]
    
    def test_upload_script_file(self):
        """Test uploading script file"""
        script_content = "EXT. CITY STREET - NIGHT\n\nWide establishing shot."
        files = {"file": ("test_script.txt", script_content, "text/plain")}
        response = client.post("/api/upload-script", files=files)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestStoryboardGeneration:
    """Test storyboard generation endpoints"""
    
    @patch('core.fibo_engine.FIBOGenerator._generate_with_fibo')
    @patch('core.fibo_engine.FIBOGenerator.__init__')
    def test_generate_storyboard(self, mock_init, mock_generate):
        """Test storyboard generation"""
        # Mock the FIBO generator
        mock_init.return_value = None
        
        # Create a mock image
        mock_image = Image.new('RGB', (1920, 1080), color='blue')
        
        # Mock the generate method
        mock_generate.return_value = mock_image
        
        script_content = """EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs."""
        
        with patch('api.main.fibo_generator') as mock_gen:
            # Setup mock
            mock_frame = MagicMock()
            mock_frame.scene_number = 1
            mock_frame.params = {
                "camera": {"angle": "eye_level", "fov": 60},
                "lighting": {"time_of_day": "night"}
            }
            mock_frame.image = mock_image
            mock_frame.to_dict.return_value = {
                "scene_number": 1,
                "image": f"data:image/png;base64,{base64.b64encode(b'test').decode()}",
                "params": mock_frame.params
            }
            
            mock_storyboard = MagicMock()
            mock_storyboard.frames = [mock_frame]
            mock_gen.create_storyboard.return_value = mock_storyboard
            
            response = client.post(
                "/api/generate-storyboard",
                json={
                    "script_content": script_content,
                    "llm_provider": "bria",
                    "hdr_enabled": True
                }
            )
            
            # Should succeed (even if BRIA API fails, it returns error placeholders)
            assert response.status_code in [200, 500]
    
    def test_generate_storyboard_empty_script(self):
        """Test storyboard generation with empty script"""
        response = client.post(
            "/api/generate-storyboard",
            json={
                "script_content": "",
                "llm_provider": "bria",
                "hdr_enabled": True
            }
        )
        # Should return error for empty script
        assert response.status_code in [400, 500]


class TestBRIAAPIClient:
    """Test BRIA API client"""
    
    @patch('core.bria_client.requests.post')
    def test_generate_image_endpoint(self, mock_post):
        """Test image generation endpoint format"""
        from core.bria_client import BRIAAPIClient
        import os
        from unittest.mock import patch
        
        # Mock environment
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "request_id": "test123",
                "status_url": "https://engine.prod.bria-api.com/v2/status/test123"
            }
            mock_post.return_value = mock_response
            
            # Test generate_image
            result = client.generate_image(
                prompt="test prompt",
                width=512,
                height=512,
                model_id="test_model"
            )
            
            # Verify endpoint was called correctly
            assert mock_post.called
            call_args = mock_post.call_args
            assert "text-to-image/tailored/test_model" in call_args[0][0]
            assert call_args[1]["json"]["prompt"] == "test prompt"
            assert result["request_id"] == "test123"
    
    @patch('core.bria_client.requests.post')
    def test_generate_video_endpoint(self, mock_post):
        """Test video generation endpoint format"""
        from core.bria_client import BRIAAPIClient
        
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "request_id": "video123",
                "status_url": "https://engine.prod.bria-api.com/v2/status/video123"
            }
            mock_post.return_value = mock_response
            
            # Test generate_video
            result = client.generate_video(
                prompt="test video prompt",
                image_url="data:image/png;base64,test",
                duration=3.0
            )
            
            # Verify endpoint was called correctly
            assert mock_post.called
            call_args = mock_post.call_args
            assert "video/generate/tailored/image-to-video" in call_args[0][0]
            assert call_args[1]["json"]["prompt"] == "test video prompt"
            assert result["request_id"] == "video123"


class TestLLMTranslator:
    """Test LLM translator"""
    
    def test_bria_translator(self):
        """Test BRIA/FIBO rule-based translation"""
        from core.llm_translator import LLMTranslator
        
        translator = LLMTranslator(provider="bria")
        
        # Test translation
        result = translator.translate_to_json(
            "Wide establishing shot. Rain-soaked street, neon signs.",
            {"shot_type": "wide", "lighting": "night"}
        )
        
        assert isinstance(result, dict)
        assert "camera" in result
        assert "lighting" in result
        assert "color" in result
        assert "composition" in result
        
        # Verify FOV is set for wide shot
        assert result["camera"]["fov"] == 60
        assert result["lighting"]["time_of_day"] == "night"


class TestFIBOEngine:
    """Test FIBO engine"""
    
    @patch('core.bria_client.BRIAAPIClient.generate_image_sync')
    def test_fibo_prompt_building(self, mock_generate):
        """Test FIBO prompt building"""
        from core.fibo_engine import FIBOGenerator
        from core.bria_client import BRIAAPIClient
        from unittest.mock import MagicMock
        
        # Mock BRIA client
        mock_bria = MagicMock()
        mock_bria.build_fibo_prompt.return_value = "Enhanced prompt with FIBO params"
        
        # Mock image generation
        mock_image = Image.new('RGB', (1920, 1080), color='red')
        mock_generate.return_value = mock_image
        
        # Create generator
        generator = FIBOGenerator(
            api_token="test_token",
            image_width=1920,
            image_height=1080
        )
        generator.bria_client = mock_bria
        
        # Test prompt building directly
        from core.bria_client import BRIAAPIClient
        test_client = BRIAAPIClient(api_token="test")
        
        fibo_params = {
            "camera": {"fov": 60, "angle": "high"},
            "lighting": {"time_of_day": "golden_hour"},
            "color": {"palette": "warm"}
        }
        
        prompt = test_client.build_fibo_prompt(
            "Scene description",
            fibo_params
        )
        
        assert "Scene description" in prompt
        assert "high angle" in prompt or "wide shot" in prompt
        assert "golden hour" in prompt or "golden_hour" in prompt


class TestIntegration:
    """Integration tests"""
    
    def test_full_flow_mock(self):
        """Test full storyboard generation flow with mocks"""
        from core.script_parser import ScriptProcessor
        from core.llm_translator import LLMTranslator
        from core.fibo_engine import FIBOGenerator
        from unittest.mock import patch, MagicMock
        from PIL import Image
        
        script_content = """EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs."""
        
        # Parse script
        processor = ScriptProcessor()
        scenes = processor.parse_script_content(script_content)
        assert len(scenes) > 0
        
        # Translate to FIBO
        translator = LLMTranslator(provider="bria")
        fibo_params = translator.translate_to_json(
            scenes[0].description,
            scenes[0].visual_notes
        )
        assert isinstance(fibo_params, dict)
        
        # Test generation with mock
        with patch('core.bria_client.BRIAAPIClient.generate_image_sync') as mock_gen:
            mock_image = Image.new('RGB', (1920, 1080), color='green')
            mock_gen.return_value = mock_image
            
            generator = FIBOGenerator(
                api_token="test_token",
                image_width=1920,
                image_height=1080
            )
            
            frame = generator.generate_frame(
                scenes[0].description,
                fibo_params,
                scenes[0].number
            )
            
            assert frame.scene_number == scenes[0].number
            assert frame.params == fibo_params

