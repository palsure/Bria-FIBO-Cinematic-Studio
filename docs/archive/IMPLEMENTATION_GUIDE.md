# FIBO Studio Implementation Guide

## Technical Architecture

### 1. Script Parser Module

**Purpose**: Extract scene information and visual directions from scripts

**Input Formats**:
- Final Draft (.fdx)
- Fountain format (.fountain)
- Plain text with scene markers

**Key Functions**:
```python
class ScriptProcessor:
    def parse_script(self, file_path: str) -> List[Scene]:
        """Parse script and extract scenes"""
        
    def extract_visual_directions(self, scene: Scene) -> Dict:
        """Extract camera, lighting, and visual notes"""
        
    def identify_shot_types(self, text: str) -> List[str]:
        """Identify shot types from scene descriptions"""
```

**Example Output**:
```json
{
  "scene_number": 1,
  "location": "EXT. CITY STREET - NIGHT",
  "description": "Wide establishing shot. Rain-soaked street...",
  "visual_notes": {
    "camera": "wide establishing shot",
    "movement": "slow push-in",
    "lighting": "neon signs, night",
    "color": "desaturated"
  }
}
```

---

### 2. LLM Translation Service

**Purpose**: Convert natural language descriptions to FIBO JSON

**Approach**:
- Use LLM (GPT-4, Claude, or local) with structured output
- Provide FIBO JSON schema as context
- Map cinematic terminology to FIBO parameters

**Prompt Template**:
```
You are a cinematography expert. Convert the following scene description 
into FIBO JSON format.

Scene: {scene_description}
Visual Notes: {visual_notes}

FIBO JSON Schema:
- camera_angle: [high, low, eye_level, dutch]
- fov: number (degrees, 10-120)
- lighting: {time_of_day, style, direction, intensity}
- color_palette: {warm, cool, desaturated, vibrant}
- composition: {rule_of_thirds, symmetry, depth_of_field}

Return valid JSON matching the FIBO schema.
```

**Example Translation**:
```
Input: "Wide establishing shot, golden hour, warm color palette"
Output: {
  "camera_angle": "eye_level",
  "fov": 60,
  "lighting": {
    "time_of_day": "golden_hour",
    "style": "soft",
    "intensity": 0.8
  },
  "color_palette": "warm"
}
```

---

### 3. FIBO Generation Engine

**Purpose**: Generate images using FIBO with JSON control

**Key Components**:

#### A. Parameter Mapping
```python
class FIBOParameterMapper:
    def map_camera_angle(self, angle: str) -> dict:
        """Map cinematic camera angle to FIBO parameters"""
        mappings = {
            "high": {"camera_angle": "high", "elevation": 45},
            "low": {"camera_angle": "low", "elevation": -30},
            "eye_level": {"camera_angle": "eye_level", "elevation": 0},
            "dutch": {"camera_angle": "dutch", "rotation": 15}
        }
        return mappings.get(angle, {})
    
    def map_lighting(self, lighting_desc: dict) -> dict:
        """Map lighting description to FIBO lighting parameters"""
        # Map time_of_day, style, direction to FIBO lighting JSON
        pass
    
    def map_color_palette(self, palette: str) -> dict:
        """Map color palette to FIBO color parameters"""
        pass
```

#### B. Consistency Engine
```python
class ConsistencyEngine:
    def __init__(self):
        self.frame_history = []
        self.character_positions = {}
        self.lighting_state = None
        
    def maintain_consistency(self, current_params: dict, 
                           previous_params: dict) -> dict:
        """Adjust parameters to maintain visual continuity"""
        # Interpolate camera positions
        # Maintain lighting continuity
        # Preserve color grading consistency
        pass
    
    def track_character(self, character: str, position: dict):
        """Track character positions across frames"""
        pass
```

#### C. Batch Generation
```python
class FIBOGenerator:
    def generate_storyboard(self, scenes: List[Scene]) -> Storyboard:
        """Generate all frames for a storyboard"""
        frames = []
        consistency_engine = ConsistencyEngine()
        
        for i, scene in enumerate(scenes):
            # Translate to JSON
            json_params = self.translate_to_json(scene)
            
            # Maintain consistency
            if i > 0:
                json_params = consistency_engine.maintain_consistency(
                    json_params, frames[-1].params
                )
            
            # Generate frame
            frame = self.generate_frame(json_params, hdr=True)
            frames.append(frame)
            
            # Update consistency tracker
            consistency_engine.update_state(json_params)
        
        return Storyboard(frames)
```

---

### 4. Export Pipeline

#### A. PDF Storyboard
```python
class PDFExporter:
    def export_storyboard(self, storyboard: Storyboard, 
                         output_path: str):
        """Export storyboard as PDF"""
        # Use ReportLab or similar
        # Layout: 3-6 frames per page
        # Include shot descriptions, camera notes
        pass
```

#### B. Animatic Video
```python
class AnimaticExporter:
    def export_animatic(self, storyboard: Storyboard, 
                       output_path: str, duration: float = 3.0):
        """Create animatic video from storyboard"""
        # Use OpenCV or FFmpeg
        # Add transitions between frames
        # Include timing from script
        pass
```

#### C. HDR Export
```python
class HDRExporter:
    def export_hdr(self, frame: Frame, output_path: str, 
                   format: str = "exr"):
        """Export frame as HDR (16-bit)"""
        # Use OpenEXR or similar
        # Maintain 16-bit color depth
        # Include metadata (camera params, lighting, etc.)
        pass
```

#### D. Nuke Script Export
```python
class NukeExporter:
    def export_nuke_script(self, storyboard: Storyboard, 
                          output_path: str):
        """Export camera and color data as Nuke script"""
        # Generate .nk file with:
        # - Camera nodes with FOV, angle data
        # - Color nodes matching FIBO color grading
        # - Read nodes for storyboard frames
        pass
```

---

### 5. Web UI / Desktop App

**Option A: Streamlit (Quick Prototype)**
```python
import streamlit as st
from fibo_studio import ScriptProcessor, FIBOGenerator

st.title("FIBO Studio")

# Upload script
script_file = st.file_uploader("Upload Script", type=['txt', 'fdx'])

if script_file:
    # Process script
    processor = ScriptProcessor()
    scenes = processor.parse_script(script_file)
    
    # Display scenes
    for scene in scenes:
        st.subheader(f"Scene {scene.number}")
        st.write(scene.description)
        
        # Generate button
        if st.button(f"Generate Storyboard for Scene {scene.number}"):
            generator = FIBOGenerator()
            storyboard = generator.create_storyboard([scene])
            
            # Display frames
            for frame in storyboard.frames:
                st.image(frame.image)
                st.json(frame.params)
```

**Option B: React + FastAPI (Production)**
- FastAPI backend for processing
- React frontend for UI
- WebSocket for real-time generation updates

---

## FIBO JSON Schema Reference

Based on FIBO documentation, structure your JSON like:

```json
{
  "prompt": "Scene description",
  "camera": {
    "angle": "eye_level",
    "fov": 60,
    "elevation": 0,
    "rotation": 0,
    "movement": "static"
  },
  "lighting": {
    "time_of_day": "golden_hour",
    "style": "soft",
    "direction": "side",
    "intensity": 0.8,
    "color_temperature": 3200
  },
  "color": {
    "palette": "warm",
    "saturation": 0.7,
    "contrast": 0.6,
    "grading": "cinematic"
  },
  "composition": {
    "rule_of_thirds": true,
    "depth_of_field": "shallow",
    "framing": "wide"
  },
  "output": {
    "resolution": [1920, 1080],
    "hdr": true,
    "bit_depth": 16
  }
}
```

---

## Implementation Checklist

### Day 1-2: Core Pipeline
- [ ] Set up FIBO model integration
- [ ] Build basic script parser
- [ ] Implement LLM translator
- [ ] Test single frame generation

### Day 2-3: Cinematic Controls
- [ ] Camera parameter system
- [ ] Lighting control
- [ ] Color palette system
- [ ] Test parameter variations

### Day 3-4: Consistency Engine
- [ ] Multi-frame tracking
- [ ] Parameter interpolation
- [ ] Visual continuity validation
- [ ] Test multi-scene generation

### Day 4-5: Professional Exports
- [ ] PDF export
- [ ] Animatic video
- [ ] HDR/16-bit export
- [ ] Nuke script export

### Day 5-6: UI & Polish
- [ ] Build web interface
- [ ] Interactive parameter editor
- [ ] Real-time preview
- [ ] Documentation
- [ ] Demo video

---

## Tips for Success

1. **Start Simple**: Get basic script → JSON → image working first
2. **Focus on Consistency**: This is FIBO's strength - showcase it
3. **HDR is Key**: Only project with HDR support wins Best Overall
4. **Show Real Workflow**: Use actual film scripts in demo
5. **Document Everything**: Clear README and examples are crucial

---

## Resources

- FIBO Hugging Face: https://huggingface.co/briaai
- FIBO API Docs: https://docs.bria.ai
- JSON Schema Examples: Check GitHub repo
- ComfyUI Integration: Use if building ComfyUI nodes




