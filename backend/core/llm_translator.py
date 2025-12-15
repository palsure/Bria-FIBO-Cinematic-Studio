"""
LLM Translation Service
Converts natural language descriptions to FIBO JSON format
"""

from typing import Dict, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()


class LLMTranslator:
    """Translates natural language to FIBO JSON using LLM"""
    
    def __init__(self, provider: str = "bria"):
        """
        Initialize translator
        
        Args:
            provider: "bria", "openai", "anthropic", or "local"
        """
        self.provider = provider
        self.api_key = self._get_api_key()
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key based on provider"""
        if self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None
    
    def translate_to_json(self, scene_description: str, 
                         visual_notes: Dict[str, str]) -> Dict:
        """
        Translate scene description to FIBO JSON
        
        Args:
            scene_description: Natural language scene description
            visual_notes: Extracted visual notes from script parser
            
        Returns:
            FIBO JSON parameters
        """
        prompt = self._build_prompt(scene_description, visual_notes)
        
        if self.provider == "openai":
            return self._translate_openai(prompt)
        elif self.provider == "anthropic":
            return self._translate_anthropic(prompt)
        elif self.provider == "bria" or self.provider == "local":
            # Use BRIA/FIBO rule-based translation (structured JSON approach)
            return self._bria_rule_based_translation(scene_description, visual_notes)
        else:
            # Fallback to basic rule-based translation
            return self._rule_based_translation(visual_notes)
    
    def _build_prompt(self, description: str, visual_notes: Dict) -> str:
        """Build prompt for LLM"""
        return f"""You are a cinematography expert. Convert the following scene description into FIBO JSON format.

Scene Description: {description}

Visual Notes: {json.dumps(visual_notes, indent=2)}

FIBO JSON Schema:
{{
  "camera": {{
    "angle": "eye_level|high|low|dutch",
    "fov": 60,  // degrees, 10-120
    "elevation": 0,  // degrees, -90 to 90
    "rotation": 0,  // degrees, -180 to 180
    "movement": "static|push_in|pull_out|pan|tilt|dolly"
  }},
  "lighting": {{
    "time_of_day": "golden_hour|blue_hour|day|night|midday",
    "style": "soft|dramatic|high_key|low_key|natural",
    "direction": "front|side|back|top|bottom",
    "intensity": 0.8,  // 0.0 to 1.0
    "color_temperature": 3200  // Kelvin
  }},
  "color": {{
    "palette": "warm|cool|desaturated|vibrant|neutral",
    "saturation": 0.7,  // 0.0 to 1.0
    "contrast": 0.6,  // 0.0 to 1.0
    "grading": "cinematic|natural|stylized"
  }},
  "composition": {{
    "rule_of_thirds": true,
    "depth_of_field": "shallow|medium|deep",
    "framing": "wide|medium|tight"
  }}
}}

Return ONLY valid JSON matching this schema. Do not include any explanation or markdown formatting.
"""
    
    def _translate_openai(self, prompt: str) -> Dict:
        """Translate using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a cinematography expert that converts scene descriptions to FIBO JSON format. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI translation error: {e}")
            return self._rule_based_translation({})
    
    def _translate_anthropic(self, prompt: str) -> Dict:
        """Translate using Anthropic API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            # Extract JSON from response
            json_str = self._extract_json(content)
            return json.loads(json_str)
        except Exception as e:
            print(f"Anthropic translation error: {e}")
            return self._rule_based_translation({})
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON in code blocks
        import re
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text
    
    def _rule_based_translation(self, visual_notes: Dict) -> Dict:
        """Fallback rule-based translation"""
        # Default FIBO JSON structure
        fibo_json = {
            "camera": {
                "angle": "eye_level",
                "fov": 60,
                "elevation": 0,
                "rotation": 0,
                "movement": "static"
            },
            "lighting": {
                "time_of_day": "day",
                "style": "natural",
                "direction": "front",
                "intensity": 0.7,
                "color_temperature": 5600
            },
            "color": {
                "palette": "neutral",
                "saturation": 0.7,
                "contrast": 0.6,
                "grading": "natural"
            },
            "composition": {
                "rule_of_thirds": True,
                "depth_of_field": "medium",
                "framing": "medium"
            }
        }
        
        # Map visual notes to FIBO parameters
        if "camera_angle" in visual_notes:
            angle_map = {
                "high": {"angle": "high", "elevation": 45},
                "low": {"angle": "low", "elevation": -30},
                "dutch": {"angle": "dutch", "rotation": 15},
                "eye_level": {"angle": "eye_level", "elevation": 0}
            }
            if visual_notes["camera_angle"] in angle_map:
                fibo_json["camera"].update(angle_map[visual_notes["camera_angle"]])
        
        if "shot_type" in visual_notes:
            fov_map = {
                "wide": 60,
                "medium": 40,
                "close": 25,
                "extreme_close": 15
            }
            if visual_notes["shot_type"] in fov_map:
                fibo_json["camera"]["fov"] = fov_map[visual_notes["shot_type"]]
        
        if "lighting" in visual_notes:
            lighting_map = {
                "golden_hour": {"time_of_day": "golden_hour", "color_temperature": 3200},
                "blue_hour": {"time_of_day": "blue_hour", "color_temperature": 6500},
                "night": {"time_of_day": "night", "intensity": 0.3},
                "day": {"time_of_day": "day", "intensity": 0.8}
            }
            if visual_notes["lighting"] in lighting_map:
                fibo_json["lighting"].update(lighting_map[visual_notes["lighting"]])
        
        if "color" in visual_notes:
            fibo_json["color"]["palette"] = visual_notes["color"]
            if visual_notes["color"] == "desaturated":
                fibo_json["color"]["saturation"] = 0.4
            elif visual_notes["color"] == "vibrant":
                fibo_json["color"]["saturation"] = 0.9
        
        return fibo_json
    
    def _bria_rule_based_translation(self, scene_description: str, visual_notes: Dict) -> Dict:
        """
        Enhanced BRIA/FIBO rule-based translation
        Uses structured approach aligned with FIBO's JSON-native design
        """
        # Start with base FIBO JSON structure
        fibo_json = {
            "camera": {
                "angle": "eye_level",
                "fov": 60,
                "elevation": 0,
                "rotation": 0,
                "movement": "static"
            },
            "lighting": {
                "time_of_day": "day",
                "style": "natural",
                "direction": "front",
                "intensity": 0.7,
                "color_temperature": 5600
            },
            "color": {
                "palette": "neutral",
                "saturation": 0.7,
                "contrast": 0.6,
                "grading": "natural"
            },
            "composition": {
                "rule_of_thirds": True,
                "depth_of_field": "medium",
                "framing": "medium"
            }
        }
        
        # Enhanced camera angle mapping
        if "camera_angle" in visual_notes:
            angle_map = {
                "high": {"angle": "high", "elevation": 45},
                "low": {"angle": "low", "elevation": -30},
                "dutch": {"angle": "dutch", "rotation": 15},
                "eye_level": {"angle": "eye_level", "elevation": 0}
            }
            if visual_notes["camera_angle"] in angle_map:
                fibo_json["camera"].update(angle_map[visual_notes["camera_angle"]])
        
        # Enhanced FOV mapping based on shot type
        if "shot_type" in visual_notes:
            fov_map = {
                "wide": 60,
                "medium": 40,
                "close": 25,
                "extreme_close": 15
            }
            if visual_notes["shot_type"] in fov_map:
                fibo_json["camera"]["fov"] = fov_map[visual_notes["shot_type"]]
        
        # Enhanced lighting mapping
        if "lighting" in visual_notes:
            lighting_map = {
                "golden_hour": {
                    "time_of_day": "golden_hour",
                    "style": "soft",
                    "color_temperature": 3200,
                    "intensity": 0.8
                },
                "blue_hour": {
                    "time_of_day": "blue_hour",
                    "style": "soft",
                    "color_temperature": 6500,
                    "intensity": 0.6
                },
                "night": {
                    "time_of_day": "night",
                    "style": "dramatic",
                    "intensity": 0.3,
                    "color_temperature": 3000
                },
                "day": {
                    "time_of_day": "day",
                    "style": "natural",
                    "intensity": 0.8,
                    "color_temperature": 5600
                }
            }
            if visual_notes["lighting"] in lighting_map:
                fibo_json["lighting"].update(lighting_map[visual_notes["lighting"]])
        
        # Enhanced color palette mapping
        if "color" in visual_notes:
            color_map = {
                "warm": {
                    "palette": "warm",
                    "saturation": 0.8,
                    "color_temperature": 3200
                },
                "cool": {
                    "palette": "cool",
                    "saturation": 0.7,
                    "color_temperature": 6500
                },
                "desaturated": {
                    "palette": "desaturated",
                    "saturation": 0.4,
                    "contrast": 0.5
                },
                "vibrant": {
                    "palette": "vibrant",
                    "saturation": 0.9,
                    "contrast": 0.7
                }
            }
            if visual_notes["color"] in color_map:
                fibo_json["color"].update(color_map[visual_notes["color"]])
            else:
                fibo_json["color"]["palette"] = visual_notes["color"]
        
        # Enhanced camera movement mapping
        if "movement" in visual_notes:
            movement_map = {
                "push_in": {"movement": "push_in", "fov": max(15, fibo_json["camera"]["fov"] - 10)},
                "pull_out": {"movement": "pull_out", "fov": min(120, fibo_json["camera"]["fov"] + 10)},
                "pan": {"movement": "pan"},
                "tilt": {"movement": "tilt"},
                "dolly": {"movement": "dolly"}
            }
            if visual_notes["movement"] in movement_map:
                fibo_json["camera"].update(movement_map[visual_notes["movement"]])
        
        # Enhanced composition based on description
        description_lower = scene_description.lower()
        if "rule of thirds" in description_lower or "composition" in description_lower:
            fibo_json["composition"]["rule_of_thirds"] = True
        
        if "shallow" in description_lower and "depth" in description_lower:
            fibo_json["composition"]["depth_of_field"] = "shallow"
        elif "deep" in description_lower and "depth" in description_lower:
            fibo_json["composition"]["depth_of_field"] = "deep"
        
        return fibo_json

