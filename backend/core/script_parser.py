"""
Script Parser Module
Extracts scene information and visual directions from scripts
"""

from typing import List, Dict, Optional
import re
from dataclasses import dataclass


@dataclass
class Scene:
    """Represents a scene from a script"""
    number: int
    location: str
    description: str
    visual_notes: Dict[str, str]
    characters: List[str]
    dialogue: Optional[str] = None


class ScriptProcessor:
    """Processes scripts and extracts scene information"""
    
    def __init__(self):
        self.shot_patterns = {
            'wide': r'(wide|establishing|long shot|full shot)',
            'medium': r'(medium shot|mid shot|two shot)',
            'close': r'(close-up|close up|tight shot)',
            'extreme_close': r'(extreme close-up|extreme close up)',
        }
        
        self.camera_patterns = {
            'high': r'(high angle|from above|overhead)',
            'low': r'(low angle|from below|looking up)',
            'dutch': r'(dutch angle|tilted|canted)',
            'eye_level': r'(eye level|straight on)',
        }
        
        self.lighting_patterns = {
            'golden_hour': r'(golden hour|sunset|sunrise|warm light)',
            'blue_hour': r'(blue hour|twilight|dusk|dawn)',
            'night': r'(night|dark|moonlight|streetlights)',
            'day': r'(day|daylight|bright|sunny)',
        }
    
    def parse_script(self, file_path: str) -> List[Scene]:
        """
        Parse a script file and extract scenes
        
        Args:
            file_path: Path to script file (.txt, .fdx, .fountain)
            
        Returns:
            List of Scene objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple scene extraction (can be enhanced for Final Draft format)
        scenes = self._extract_scenes(content)
        
        return scenes
    
    def parse_script_content(self, content: str) -> List[Scene]:
        """
        Parse script content from string
        
        Args:
            content: Script content as string
            
        Returns:
            List of Scene objects
        """
        scenes = self._extract_scenes(content)
        return scenes
    
    def _extract_scenes(self, content: str) -> List[Scene]:
        """Extract scenes from script content"""
        scenes = []
        
        # Pattern to match scene headers (INT./EXT. LOCATION - TIME)
        scene_pattern = r'(INT\.|EXT\.)\s+([^-]+)\s*-\s*([^\n]+)'
        matches = re.finditer(scene_pattern, content, re.IGNORECASE)
        
        scene_number = 1
        for match in matches:
            scene_type = match.group(1)
            location = match.group(2).strip()
            time = match.group(3).strip()
            
            # Extract description until next scene or action
            start_pos = match.end()
            next_match = None
            for next_match_iter in re.finditer(scene_pattern, content[start_pos:], re.IGNORECASE):
                next_match = next_match_iter
                break
            
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = len(content)
            
            description = content[start_pos:end_pos].strip()
            
            # Extract visual notes
            visual_notes = self._extract_visual_directions(description)
            
            scene = Scene(
                number=scene_number,
                location=f"{scene_type} {location} - {time}",
                description=description,
                visual_notes=visual_notes,
                characters=self._extract_characters(description)
            )
            
            scenes.append(scene)
            scene_number += 1
        
        return scenes
    
    def _extract_visual_directions(self, text: str) -> Dict[str, str]:
        """Extract visual directions from scene description"""
        visual_notes = {}
        
        # Extract shot type
        for shot_type, pattern in self.shot_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                visual_notes['shot_type'] = shot_type
                break
        
        # Extract camera angle
        for angle, pattern in self.camera_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                visual_notes['camera_angle'] = angle
                break
        
        # Extract lighting
        for lighting, pattern in self.lighting_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                visual_notes['lighting'] = lighting
                break
        
        # Extract camera movement
        if re.search(r'(push|push-in|push in)', text, re.IGNORECASE):
            visual_notes['movement'] = 'push_in'
        elif re.search(r'(pull|pull-out|pull out)', text, re.IGNORECASE):
            visual_notes['movement'] = 'pull_out'
        elif re.search(r'(pan|pans)', text, re.IGNORECASE):
            visual_notes['movement'] = 'pan'
        elif re.search(r'(tilt|tilts)', text, re.IGNORECASE):
            visual_notes['movement'] = 'tilt'
        elif re.search(r'(dolly|track)', text, re.IGNORECASE):
            visual_notes['movement'] = 'dolly'
        
        # Extract color notes
        if re.search(r'(warm|golden|orange)', text, re.IGNORECASE):
            visual_notes['color'] = 'warm'
        elif re.search(r'(cool|blue|cyan)', text, re.IGNORECASE):
            visual_notes['color'] = 'cool'
        elif re.search(r'(desaturated|muted|gray)', text, re.IGNORECASE):
            visual_notes['color'] = 'desaturated'
        elif re.search(r'(vibrant|saturated|colorful)', text, re.IGNORECASE):
            visual_notes['color'] = 'vibrant'
        
        return visual_notes
    
    def _extract_characters(self, text: str) -> List[str]:
        """Extract character names from scene (simplified)"""
        # This is a simplified version - can be enhanced
        characters = []
        # Look for character names in ALL CAPS (common script format)
        char_pattern = r'^([A-Z][A-Z\s]+)$'
        for line in text.split('\n'):
            match = re.match(char_pattern, line.strip())
            if match:
                characters.append(match.group(1).strip())
        return characters





