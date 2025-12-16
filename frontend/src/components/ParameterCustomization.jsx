import React, { useState } from 'react'
import './ParameterCustomization.css'

const DEFAULT_PARAMS = {
  camera: {
    angle: 'eye_level',
    fov: 50,
    elevation: 0,
    rotation: 0,
    movement: 'static'
  },
  lighting: {
    time_of_day: 'day',
    style: 'natural',
    direction: 'front',
    intensity: 0.7,
    color_temperature: 5600
  },
  color: {
    palette: 'neutral',
    saturation: 0.7,
    contrast: 0.6,
    grading: 'natural'
  },
  composition: {
    rule_of_thirds: true,
    depth_of_field: 'medium',
    framing: 'medium'
  }
}

function ParameterCustomization({ params, onChange, onReset }) {
  const [localParams, setLocalParams] = useState(params || DEFAULT_PARAMS)
  const [isExpanded, setIsExpanded] = useState(true)

  const updateParam = (category, key, value) => {
    const newParams = {
      ...localParams,
      [category]: {
        ...localParams[category],
        [key]: value
      }
    }
    setLocalParams(newParams)
    if (onChange) onChange(newParams)
  }

  const handleReset = () => {
    setLocalParams(DEFAULT_PARAMS)
    if (onReset) onReset(DEFAULT_PARAMS)
    if (onChange) onChange(DEFAULT_PARAMS)
  }

  return (
    <div className="parameter-customization">
      <div className="parameter-content">
          {/* Camera Parameters */}
          <div className="param-section">
            <h4>📷 Camera</h4>
            <div className="param-grid">
              <div className="param-item">
                <label>Angle:</label>
                <select
                  value={localParams.camera.angle}
                  onChange={(e) => updateParam('camera', 'angle', e.target.value)}
                >
                  <option value="eye_level">Eye Level</option>
                  <option value="high">High</option>
                  <option value="low">Low</option>
                  <option value="dutch">Dutch</option>
                  <option value="bird_eye">Bird's Eye</option>
                  <option value="worm_eye">Worm's Eye</option>
                </select>
              </div>

              <div className="param-item">
                <label>FOV: {localParams.camera.fov}°</label>
                <input
                  type="range"
                  min="15"
                  max="90"
                  value={localParams.camera.fov}
                  onChange={(e) => updateParam('camera', 'fov', parseInt(e.target.value))}
                />
              </div>

              <div className="param-item">
                <label>Elevation: {localParams.camera.elevation}°</label>
                <input
                  type="range"
                  min="-45"
                  max="45"
                  value={localParams.camera.elevation}
                  onChange={(e) => updateParam('camera', 'elevation', parseInt(e.target.value))}
                />
              </div>

              <div className="param-item">
                <label>Movement:</label>
                <select
                  value={localParams.camera.movement}
                  onChange={(e) => updateParam('camera', 'movement', e.target.value)}
                >
                  <option value="static">Static</option>
                  <option value="pan_left">Pan Left</option>
                  <option value="pan_right">Pan Right</option>
                  <option value="tilt_up">Tilt Up</option>
                  <option value="tilt_down">Tilt Down</option>
                  <option value="push_in">Push In</option>
                  <option value="pull_out">Pull Out</option>
                </select>
              </div>
            </div>
          </div>

          {/* Lighting Parameters */}
          <div className="param-section">
            <h4>💡 Lighting</h4>
            <div className="param-grid">
              <div className="param-item">
                <label>Time of Day:</label>
                <select
                  value={localParams.lighting.time_of_day}
                  onChange={(e) => updateParam('lighting', 'time_of_day', e.target.value)}
                >
                  <option value="day">Day</option>
                  <option value="night">Night</option>
                  <option value="dawn">Dawn</option>
                  <option value="dusk">Dusk</option>
                  <option value="golden_hour">Golden Hour</option>
                  <option value="blue_hour">Blue Hour</option>
                </select>
              </div>

              <div className="param-item">
                <label>Style:</label>
                <select
                  value={localParams.lighting.style}
                  onChange={(e) => updateParam('lighting', 'style', e.target.value)}
                >
                  <option value="natural">Natural</option>
                  <option value="dramatic">Dramatic</option>
                  <option value="soft">Soft</option>
                  <option value="hard">Hard</option>
                  <option value="rim">Rim</option>
                  <option value="backlit">Backlit</option>
                </select>
              </div>

              <div className="param-item">
                <label>Direction:</label>
                <select
                  value={localParams.lighting.direction}
                  onChange={(e) => updateParam('lighting', 'direction', e.target.value)}
                >
                  <option value="front">Front</option>
                  <option value="side">Side</option>
                  <option value="back">Back</option>
                  <option value="top">Top</option>
                  <option value="bottom">Bottom</option>
                </select>
              </div>

              <div className="param-item">
                <label>Intensity: {localParams.lighting.intensity.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localParams.lighting.intensity}
                  onChange={(e) => updateParam('lighting', 'intensity', parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>

          {/* Color Parameters */}
          <div className="param-section">
            <h4>🎨 Color</h4>
            <div className="param-grid">
              <div className="param-item">
                <label>Palette:</label>
                <select
                  value={localParams.color.palette}
                  onChange={(e) => updateParam('color', 'palette', e.target.value)}
                >
                  <option value="neutral">Neutral</option>
                  <option value="warm">Warm</option>
                  <option value="cool">Cool</option>
                  <option value="desaturated">Desaturated</option>
                  <option value="vibrant">Vibrant</option>
                  <option value="monochrome">Monochrome</option>
                </select>
              </div>

              <div className="param-item">
                <label>Saturation: {localParams.color.saturation.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localParams.color.saturation}
                  onChange={(e) => updateParam('color', 'saturation', parseFloat(e.target.value))}
                />
              </div>

              <div className="param-item">
                <label>Contrast: {localParams.color.contrast.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={localParams.color.contrast}
                  onChange={(e) => updateParam('color', 'contrast', parseFloat(e.target.value))}
                />
              </div>

              <div className="param-item">
                <label>Grading:</label>
                <select
                  value={localParams.color.grading}
                  onChange={(e) => updateParam('color', 'grading', e.target.value)}
                >
                  <option value="natural">Natural</option>
                  <option value="cinematic">Cinematic</option>
                  <option value="vintage">Vintage</option>
                  <option value="high_contrast">High Contrast</option>
                  <option value="low_contrast">Low Contrast</option>
                </select>
              </div>
            </div>
          </div>

          {/* Composition Parameters */}
          <div className="param-section">
            <h4>📐 Composition</h4>
            <div className="param-grid">
              <div className="param-item">
                <label>
                  Rule of Thirds
                  <input
                    type="checkbox"
                    checked={localParams.composition.rule_of_thirds}
                    onChange={(e) => updateParam('composition', 'rule_of_thirds', e.target.checked)}
                  />
                </label>
              </div>

              <div className="param-item">
                <label>Depth of Field:</label>
                <select
                  value={localParams.composition.depth_of_field}
                  onChange={(e) => updateParam('composition', 'depth_of_field', e.target.value)}
                >
                  <option value="shallow">Shallow</option>
                  <option value="medium">Medium</option>
                  <option value="deep">Deep</option>
                </select>
              </div>

              <div className="param-item">
                <label>Framing:</label>
                <select
                  value={localParams.composition.framing}
                  onChange={(e) => updateParam('composition', 'framing', e.target.value)}
                >
                  <option value="tight">Tight</option>
                  <option value="medium">Medium</option>
                  <option value="wide">Wide</option>
                </select>
              </div>
            </div>
          </div>

          <div className="param-actions">
            <button onClick={handleReset} className="reset-button">
              🔄 Reset to Defaults
            </button>
          </div>
      </div>
    </div>
  )
}

export default ParameterCustomization

