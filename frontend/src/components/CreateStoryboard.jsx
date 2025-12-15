import React, { useState, useEffect } from 'react'
import axios from 'axios'
import ParameterCustomization from './ParameterCustomization'
import StoryboardViewer from './StoryboardViewer'
import './CreateStoryboard.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

function CreateStoryboard({ loadedStoryboard, onStoryboardGenerated, onError, onLoading }) {
  const [currentStep, setCurrentStep] = useState(1)
  const [scriptContent, setScriptContent] = useState(SAMPLE_SCRIPT)
  const [llmProvider, setLlmProvider] = useState('bria')
  const [hdrEnabled, setHdrEnabled] = useState(true)
  const [customParams, setCustomParams] = useState(null)
  const [storyboard, setStoryboard] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [parsedScenes, setParsedScenes] = useState(null)

  // Handle loaded storyboard from parent
  useEffect(() => {
    if (loadedStoryboard && loadedStoryboard.frames) {
      setStoryboard(loadedStoryboard)
      setCurrentStep(2) // Move to generation step
      // If script content is available in loaded storyboard, set it
      if (loadedStoryboard.script_content) {
        setScriptContent(loadedStoryboard.script_content)
      }
    }
  }, [loadedStoryboard])

  const steps = [
    { number: 1, title: 'Scripting', icon: '📝' },
    { number: 2, title: 'Scene Generation and Editing', icon: '🎬' }
  ]

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      setLoading(true)
      setError(null)
      const response = await axios.post(`${API_BASE_URL}/api/upload-script`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Read file content for generation
      const fileContent = await file.text()
      setScriptContent(fileContent)
      setParsedScenes(response.data)
      setCurrentStep(2) // Move to generation step
      // Auto-generate storyboard after parsing
      await handleAutoGenerateStoryboard(response.data)
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleScriptSubmit = async () => {
    if (!scriptContent.trim()) {
      setError('Please enter script content')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const response = await axios.post(`${API_BASE_URL}/api/parse-script`, {
        content: scriptContent,
      })

      setParsedScenes(response.data)
      setCurrentStep(2) // Move to generation step
      // Auto-generate storyboard after parsing
      await handleAutoGenerateStoryboard(response.data)
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAutoGenerateStoryboard = async (scenes) => {
    if (!scriptContent.trim() || !scenes) {
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const payload = {
        script_content: scriptContent,
        llm_provider: llmProvider,
        hdr_enabled: hdrEnabled,
      }
      
      if (customParams) {
        payload.custom_params = customParams
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-storyboard`, payload)

      setStoryboard(response.data)
      if (onStoryboardGenerated) {
        onStoryboardGenerated(response.data)
      }
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
      if (onLoading) {
        onLoading(false)
      }
    }
  }

  const handleGenerateStoryboard = async () => {
    if (!scriptContent.trim()) {
      setError('Please enter script content')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const payload = {
        script_content: scriptContent,
        llm_provider: llmProvider,
        hdr_enabled: hdrEnabled,
      }
      
      if (customParams) {
        payload.custom_params = customParams
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-storyboard`, payload)

      setStoryboard(response.data)
      // Stay on step 2 to show generated storyboard
      if (onStoryboardGenerated) {
        onStoryboardGenerated(response.data)
      }
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
      if (onLoading) {
        onLoading(false)
      }
    }
  }

  const handleExportPDF = async () => {
    try {
      setLoading(true)
      const response = await axios.post(
        `${API_BASE_URL}/api/export-pdf`,
        {
          script_content: scriptContent,
          llm_provider: llmProvider,
          hdr_enabled: hdrEnabled,
          custom_params: customParams,
        },
        {
          responseType: 'blob',
        }
      )

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'storyboard.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExportAnimatic = async () => {
    try {
      setLoading(true)
      const response = await axios.post(
        `${API_BASE_URL}/api/export-animatic`,
        {
          script_content: scriptContent,
          llm_provider: llmProvider,
          hdr_enabled: hdrEnabled,
          custom_params: customParams,
        },
        {
          responseType: 'blob',
        }
      )

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'animatic.mp4')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      setError(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleReset = () => {
    setCurrentStep(1)
    setStoryboard(null)
    setParsedScenes(null)
    setCustomParams(null)
    setError(null)
  }

  return (
    <div className="create-storyboard">
      {/* Step Indicator */}
      <div className="step-indicator">
        {steps.map((step, index) => (
          <React.Fragment key={step.number}>
            <div className={`step-item ${currentStep === step.number ? 'active' : ''} ${currentStep > step.number ? 'completed' : ''}`}>
              <div className="step-icon">{step.icon}</div>
              <div className="step-content">
                <div className="step-title">Step {step.number}: {step.title}</div>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className={`step-connector ${currentStep > step.number ? 'completed' : ''}`}></div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step Content */}
      <div className="step-content-area">
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => setError(null)} className="close-error">×</button>
          </div>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        )}

        {/* Step 1: Script */}
        {currentStep === 1 && (
          <div className="step-panel">
            <div className="description-with-upload">
              <p className="step-description">Start by uploading a script file or entering your script content below.</p>
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
            </div>
            
            <div className="upload-section">
              <div className="text-input">
                <textarea
                  value={scriptContent}
                  onChange={(e) => setScriptContent(e.target.value)}
                  placeholder="Paste your script here..."
                  rows={15}
                  className="script-textarea"
                />
              </div>
            </div>

            <div className="step-actions">
              <button onClick={handleScriptSubmit} className="next-button" disabled={loading || !scriptContent.trim()}>
                Next: Scene Generation and Editing →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Scene Generation and Editing */}
        {currentStep === 2 && (
          <div className="step-panel">
            {loading && !storyboard ? (
              <div className="generating-state">
                <div className="spinner"></div>
                <p>Generating storyboard from script...</p>
              </div>
            ) : storyboard ? (
              <>
                <p className="step-description">Review and edit your generated scenes. Adjust camera, lighting, and color parameters to fine-tune individual scenes.</p>

                <div className="editing-options">
                  <div className="hdr-option">
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

                <StoryboardViewer 
                  storyboard={storyboard}
                  parsedScenes={parsedScenes}
                  onSaveStoryboard={(data) => {
                    console.log('Storyboard saved:', data)
                  }}
                  onExportPDF={handleExportPDF}
                  onExportAnimatic={handleExportAnimatic}
                  exportLoading={loading}
                  onStoryboardUpdate={(updatedStoryboard) => {
                    setStoryboard(updatedStoryboard)
                    if (onStoryboardGenerated) {
                      onStoryboardGenerated(updatedStoryboard)
                    }
                  }}
                />

                <div className="step-actions">
                  <button onClick={handlePrevious} className="previous-button">
                    ← Back to Scripting
                  </button>
                  <button onClick={handleReset} className="reset-button">
                    🔄 Create New Storyboard
                  </button>
                </div>
              </>
            ) : (
              <div className="generate-prompt">
                <p>Processing script...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default CreateStoryboard

