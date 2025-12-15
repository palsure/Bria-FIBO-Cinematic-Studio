# BRIA/FIBO Translation System

## Overview

Since BRIA AI doesn't provide an LLM service for natural language translation, we use an **enhanced rule-based translation system** that follows BRIA/FIBO's structured JSON-native approach.

## Why BRIA/FIBO Rule-based?

1. **JSON-Native Design**: FIBO is designed for structured JSON control, not free-form text
2. **Deterministic Results**: Rule-based translation ensures consistent, predictable outputs
3. **No External Dependencies**: Works without OpenAI/Anthropic API keys
4. **Aligned with BRIA**: Uses the same structured approach as BRIA's image generation

## How It Works

### 1. Script Parsing
Extracts visual notes from script:
- Shot types (wide, medium, close-up)
- Camera angles (high, low, eye-level, dutch)
- Lighting conditions (golden hour, blue hour, night, day)
- Color palettes (warm, cool, desaturated, vibrant)
- Camera movements (push-in, pull-out, pan, tilt, dolly)

### 2. Enhanced Rule-Based Translation
Maps extracted notes to FIBO JSON parameters:

```python
# Example mapping
"golden_hour" → {
    "time_of_day": "golden_hour",
    "style": "soft",
    "color_temperature": 3200,
    "intensity": 0.8
}
```

### 3. Structured FIBO JSON Output
Produces deterministic JSON that BRIA API can use directly:

```json
{
  "camera": {
    "angle": "high",
    "fov": 60,
    "movement": "push_in"
  },
  "lighting": {
    "time_of_day": "golden_hour",
    "style": "soft",
    "intensity": 0.8
  },
  "color": {
    "palette": "warm",
    "saturation": 0.8
  }
}
```

## Advantages

### ✅ Deterministic
- Same input always produces same output
- No variability from LLM randomness
- Perfect for production workflows

### ✅ Fast
- No API calls to external LLMs
- Instant translation
- No rate limits

### ✅ Cost-Effective
- No API costs
- No token usage
- Free to use

### ✅ BRIA-Aligned
- Uses FIBO's JSON-native structure
- Direct compatibility with BRIA API
- Structured, not free-form

## When to Use Other Providers

Use OpenAI/Anthropic when:
- You need more nuanced interpretation
- Script has complex, ambiguous descriptions
- You want creative variations
- You have API credits available

Use BRIA/FIBO (default) when:
- You want deterministic results
- Script has clear visual directions
- You want fast, free translation
- You're building production workflows

## Enhanced Features

The BRIA/FIBO translator includes:

1. **Smart FOV Adjustment**: Automatically adjusts FOV based on camera movements
2. **Color Temperature Mapping**: Maps lighting conditions to accurate color temperatures
3. **Intensity Calibration**: Sets appropriate intensity based on time of day
4. **Composition Detection**: Extracts composition hints from descriptions
5. **Movement Integration**: Combines camera movements with FOV changes

## Example

**Input Script:**
```
EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs.
Camera slowly pushes in.

CLOSE-UP: Figure's face. Dramatic side lighting. Desaturated colors.
```

**Extracted Visual Notes:**
- Scene 1: wide shot, night, push_in movement
- Scene 2: close-up, dramatic lighting, desaturated colors

**FIBO JSON Output:**
```json
{
  "camera": {"fov": 60, "movement": "push_in"},
  "lighting": {"time_of_day": "night", "intensity": 0.3},
  "color": {"palette": "desaturated", "saturation": 0.4}
}
```

## Conclusion

The BRIA/FIBO rule-based translation system provides a **production-ready, deterministic, and cost-effective** solution that aligns perfectly with BRIA's structured JSON-native approach. It's the recommended default for most use cases.




