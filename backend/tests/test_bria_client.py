"""
Unit tests for BRIA API client
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import os
from core.bria_client import BRIAAPIClient
from PIL import Image
import requests


class TestBRIAAPIClientInit:
    """Test BRIA client initialization"""
    
    def test_init_with_token(self):
        """Test initialization with API token"""
        with patch.dict(os.environ, {'BRIA_API_TOKEN': 'test_token'}):
            client = BRIAAPIClient(api_token="custom_token")
            assert client.api_token == "custom_token"
            assert "api_token" in client.headers
            assert client.headers["api_token"] == "custom_token"
    
    def test_init_without_token(self):
        """Test initialization without token raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="BRIA_API_TOKEN is required"):
                BRIAAPIClient()
    
    def test_base_url_from_env(self):
        """Test base URL from environment"""
        # BASE_URL is read at class definition time via os.getenv
        # This test verifies the default behavior
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token'
        }):
            client = BRIAAPIClient()
            # Should use default or env var if set
            assert "bria-api.com" in client.BASE_URL or "bria.ai" in client.BASE_URL


class TestImageGeneration:
    """Test image generation methods"""
    
    @patch('core.bria_client.requests.post')
    def test_generate_image_async(self, mock_post):
        """Test async image generation"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "request_id": "req123",
                "status_url": "https://engine.prod.bria-api.com/v2/status/req123"
            }
            mock_post.return_value = mock_response
            
            result = client.generate_image(
                prompt="test prompt",
                width=512,
                height=512,
                model_id="test_model",
                sync=False
            )
            
            # Verify request
            assert mock_post.called
            call_url = mock_post.call_args[0][0]
            assert "text-to-image/tailored/test_model" in call_url
            
            call_data = mock_post.call_args[1]["json"]
            assert call_data["prompt"] == "test prompt"
            assert call_data["width"] == 512
            assert call_data["height"] == 512
            assert call_data["sync"] is False
            
            # Verify response
            assert result["request_id"] == "req123"
    
    @patch('core.bria_client.requests.post')
    def test_generate_image_sync(self, mock_post):
        """Test sync image generation"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock sync response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "image_url": "https://example.com/image.png"
            }
            mock_post.return_value = mock_response
            
            # Mock image download
            with patch.object(client, '_download_image') as mock_download:
                mock_image = Image.new('RGB', (512, 512))
                mock_download.return_value = mock_image
                
                result = client.generate_image(
                    prompt="test",
                    sync=True,
                    model_id="test_model"
                )
                
                call_data = mock_post.call_args[1]["json"]
                assert call_data["sync"] is True
    
    @patch('core.bria_client.requests.post')
    @patch('core.bria_client.requests.get')
    def test_generate_image_sync_async_fallback(self, mock_get, mock_post):
        """Test sync generation with async fallback"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock async response (sync fails, falls back to async)
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.json.return_value = {
                "request_id": "req456",
                "status_url": "https://engine.prod.bria-api.com/v2/status/req456"
            }
            mock_post.return_value = mock_post_response
            
            # Mock status check
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.side_effect = [
                {"status": "IN_PROGRESS"},
                {"status": "COMPLETED", "result": {"image_url": "https://example.com/img.png"}}
            ]
            mock_get.return_value = mock_get_response
            
            # Mock image download
            with patch.object(client, '_download_image') as mock_download:
                mock_image = Image.new('RGB', (512, 512))
                mock_download.return_value = mock_image
                
                result = client.generate_image_sync(
                    prompt="test",
                    model_id="test_model"
                )
                
                assert isinstance(result, Image.Image)


class TestStatusChecking:
    """Test status checking methods"""
    
    @patch('core.bria_client.requests.get')
    def test_check_status(self, mock_get):
        """Test status check"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "COMPLETED",
                "result": {"image_url": "https://example.com/img.png"}
            }
            mock_get.return_value = mock_response
            
            result = client.check_status("req123")
            
            assert mock_get.called
            call_url = mock_get.call_args[0][0]
            assert "status/req123" in call_url
            assert result["status"] == "COMPLETED"
    
    @patch('core.bria_client.requests.get')
    def test_wait_for_completion(self, mock_get):
        """Test waiting for completion"""
        import time
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Mock status progression
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = [
                {"status": "IN_PROGRESS"},
                {"status": "IN_PROGRESS"},
                {"status": "COMPLETED", "result": {"image_url": "https://example.com/img.png"}}
            ]
            mock_get.return_value = mock_response
            
            with patch('time.sleep'):  # Speed up test
                result = client.wait_for_completion("req123", max_wait=10, poll_interval=0.1)
                assert result["status"] == "COMPLETED"


class TestPromptBuilding:
    """Test prompt building"""
    
    def test_build_fibo_prompt(self):
        """Test FIBO prompt building"""
        with patch.dict(os.environ, {'BRIA_API_TOKEN': 'test_token'}):
            client = BRIAAPIClient()
            
            scene_description = "Wide establishing shot. Rain-soaked street."
            fibo_params = {
                "camera": {
                    "angle": "high",
                    "fov": 60,
                    "movement": "push_in"
                },
                "lighting": {
                    "time_of_day": "golden_hour",
                    "style": "soft"
                },
                "color": {
                    "palette": "warm"
                }
            }
            
            prompt = client.build_fibo_prompt(scene_description, fibo_params)
            
            assert scene_description in prompt
            assert "high angle" in prompt or "wide shot" in prompt
            assert "golden hour" in prompt or "golden_hour" in prompt
            assert "warm" in prompt.lower()


class TestVideoGeneration:
    """Test video generation"""
    
    @patch('core.bria_client.requests.post')
    def test_generate_video_endpoint(self, mock_post):
        """Test video generation endpoint"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "request_id": "video123",
                "status_url": "https://engine.prod.bria-api.com/v2/status/video123"
            }
            mock_post.return_value = mock_response
            
            result = client.generate_video(
                prompt="test video",
                image_url="data:image/png;base64,test",
                duration=3.0
            )
            
            call_url = mock_post.call_args[0][0]
            assert "video/generate/tailored/image-to-video" in call_url
            
            call_data = mock_post.call_args[1]["json"]
            assert call_data["prompt"] == "test video"
            assert call_data["image_url"] == "data:image/png;base64,test"
            assert call_data["duration"] == 3.0


class TestErrorHandling:
    """Test error handling"""
    
    @patch('core.bria_client.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            # Test HTTP error
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Unauthorized"}
            mock_response.text = "Unauthorized"
            
            # Create HTTPError with response
            http_error = requests.exceptions.HTTPError()
            http_error.response = mock_response
            mock_post.side_effect = http_error
            
            with pytest.raises(Exception, match="BRIA API HTTP error"):
                client.generate_image("test", model_id="test_model")
    
    @patch('core.bria_client.requests.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling"""
        with patch.dict(os.environ, {
            'BRIA_API_TOKEN': 'test_token',
            'BRIA_API_BASE_URL': 'https://engine.prod.bria-api.com/v2'
        }):
            client = BRIAAPIClient()
            
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            with pytest.raises(Exception, match="BRIA API request failed"):
                client.generate_image("test", model_id="test_model")

