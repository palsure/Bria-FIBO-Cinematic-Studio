import React, { useState } from 'react'
import axios from 'axios'
import ParameterCustomization from './ParameterCustomization'
import './ScriptUpload.css'

// Use environment variable if set, otherwise use Render backend (production) or localhost (dev)
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://fibo-backend-jb9q.onrender.com')

// Sample script for pre-population
const SAMPLE_SCRIPT = `FADE IN:

EXT. CITY STREET - NIGHT

Wide establishing shot. A rain-soaked street glistens under neon signs. 
Reflections dance in puddles. The camera slowly pushes in as a mysterious 
figure emerges from the shadows.

CLOSE-UP: The figure's face. Dramatic side lighting creates deep shadows. 
Desaturated colors. The figure's eyes catch the neon light.

EXT. ROOFTOP - GOLDEN HOUR

High angle shot looking down. The city sprawls below, bathed in warm 
golden light. The camera tilts up to reveal the skyline.

MEDIUM SHOT: Two characters stand at the edge. Warm color palette. 
Soft, natural lighting. The sun sets behind them.

FADE OUT.`

function ScriptUpload({ onStoryboardGenerated, onError, onLoading }) {
  const [scriptContent, setScriptContent] = useState(SAMPLE_SCRIPT)
  const [llmProvider, setLlmProvider] = useState('bria')
  const [hdrEnabled, setHdrEnabled] = useState(true)
  const [customParams, setCustomParams] = useState(null)

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      onLoading(true)
      const response = await axios.post(`${API_BASE_URL}/api/upload-script`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Auto-generate storyboard after parsing
      await generateStoryboard(response.data)
    } catch (error) {
      onError(error.response?.data?.detail || error.message)
      onLoading(false)
    }
  }

  const handleTextSubmit = async () => {
    if (!scriptContent.trim()) {
      onError('Please enter script content')
      return
    }

    try {
      onLoading(true)
      const response = await axios.post(`${API_BASE_URL}/api/parse-script`, {
        content: scriptContent,
      })

      // Auto-generate storyboard after parsing
      await generateStoryboard(response.data)
    } catch (error) {
      onError(error.response?.data?.detail || error.message)
      onLoading(false)
    }
  }

  const generateStoryboard = async (scenes) => {
    try {
      const payload = {
        script_content: scriptContent || scenes.map(s => s.description).join('\n\n'),
        llm_provider: llmProvider,
        hdr_enabled: hdrEnabled,
      }
      
      // Add custom parameters if provided
      if (customParams) {
        payload.custom_params = customParams
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-storyboard`, payload)

      onStoryboardGenerated(response.data)
    } catch (error) {
      onError(error.response?.data?.detail || error.message)
    } finally {
      onLoading(false)
    }
  }

  const handleExportPDF = async () => {
    try {
      onLoading(true)
      const response = await axios.post(
        `${API_BASE_URL}/api/export-pdf`,
        {
          script_content: scriptContent,
          llm_provider: llmProvider,
          hdr_enabled: hdrEnabled,
        },
        {
          responseType: 'blob',
        }
      )

      // Download PDF
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'storyboard.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      onError(error.response?.data?.detail || error.message)
    } finally {
      onLoading(false)
    }
  }

  const handleExportAnimatic = async () => {
    try {
      onLoading(true)
      const response = await axios.post(
        `${API_BASE_URL}/api/export-animatic`,
        {
          script_content: scriptContent,
          llm_provider: llmProvider,
          hdr_enabled: hdrEnabled,
        },
        {
          responseType: 'blob',
        }
      )

      // Download video
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'animatic.mp4')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      onError(error.response?.data?.detail || error.message)
    } finally {
      onLoading(false)
    }
  }

  return (
    <div className="script-upload">
      <div className="upload-section">
        <h2>Upload Script</h2>
        
        <div className="upload-options">
          <div className="file-upload">
            <label htmlFor="file-upload" className="upload-button">
              📄 Upload Script File
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".txt,.fdx,.fountain"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>

          <div className="divider">OR</div>

          <div className="text-input">
            <textarea
              value={scriptContent}
              onChange={(e) => setScriptContent(e.target.value)}
              placeholder="Paste your script here or use the sample script below..."
              rows={12}
              className="script-textarea"
            />
            <button onClick={handleTextSubmit} className="submit-button">
              Generate Storyboard
            </button>
          </div>
        </div>

        <div className="options">
          <div className="option-group">
            <label>LLM Provider:</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
            >
              <option value="bria">BRIA/FIBO Rule-based (Recommended)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="local">Local (Rule-based)</option>
            </select>
          </div>

          <div className="option-group">
            <label>
              <input
                type="checkbox"
                checked={hdrEnabled}
                onChange={(e) => setHdrEnabled(e.target.checked)}
              />
              Enable HDR/16-bit
            </label>
          </div>
        </div>

        <ParameterCustomization
          params={customParams}
          onChange={setCustomParams}
          onReset={() => setCustomParams(null)}
        />

        {scriptContent && (
          <div className="export-buttons">
            <button onClick={handleExportPDF} className="export-button">
              📄 Export PDF
            </button>
            <button onClick={handleExportAnimatic} className="export-button">
              🎬 Export Animatic
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ScriptUpload

