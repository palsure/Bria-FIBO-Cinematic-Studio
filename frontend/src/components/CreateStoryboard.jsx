import React, { useState, useEffect } from 'react'
import axios from 'axios'
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
  const [isSavedStoryboard, setIsSavedStoryboard] = useState(false)

  // Handle loaded storyboard from parent
  // IMPORTANT: Only treat as "loaded" if it has an 'id' or 'storyboard_id' (indicating it was saved)
  useEffect(() => {
    // Only process if loadedStoryboard is explicitly provided AND has an id (saved storyboard)
    if (loadedStoryboard && loadedStoryboard.frames && Array.isArray(loadedStoryboard.frames) && loadedStoryboard.frames.length > 0) {
      // Check if this is a saved storyboard (has id) vs a newly generated one
      const isSaved = !!(loadedStoryboard.id || loadedStoryboard.storyboard_id || loadedStoryboard.name)
      
      if (isSaved) {
        console.log('CreateStoryboard: Loading saved storyboard (has id/name), setting isSavedStoryboard=true', loadedStoryboard)
        setStoryboard(loadedStoryboard)
        setIsSavedStoryboard(true)
        setCurrentStep(2) // Move to generation step
        // If script content is available in loaded storyboard, set it
        if (loadedStoryboard.script_content) {
          setScriptContent(loadedStoryboard.script_content)
        }
      } else {
        // This is a newly generated storyboard, not a saved one
        console.log('CreateStoryboard: Newly generated storyboard (no id), setting isSavedStoryboard=false', loadedStoryboard)
        setStoryboard(loadedStoryboard)
        setIsSavedStoryboard(false)
        setCurrentStep(2) // Move to generation step
      }
    } else {
      // Explicitly set to false when no loaded storyboard OR when loadedStoryboard is cleared
      // Only log if we're actually clearing (not on initial mount)
      if (loadedStoryboard === null || loadedStoryboard === undefined) {
        console.log('CreateStoryboard: No loaded storyboard, ensuring isSavedStoryboard=false')
        setIsSavedStoryboard(false)
      }
    }
  }, [loadedStoryboard])

  const steps = [
    { number: 1, title: 'StoryBoard-Scripting', icon: '📝' },
    { number: 2, title: 'StoryBoard-Generation and Editing', icon: '🎬' }
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
      console.log('CreateStoryboard: Auto-generating storyboard, setting isSavedStoryboard=false')
      setIsSavedStoryboard(false) // Ensure it's not marked as saved for new generation
      
      const payload = {
        script_content: scriptContent,
        llm_provider: llmProvider,
        hdr_enabled: hdrEnabled,
      }
      
      if (customParams) {
        payload.custom_params = customParams
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-storyboard`, payload)

      console.log('CreateStoryboard: Storyboard generated, explicitly setting isSavedStoryboard=false')
      // CRITICAL: Set to false BEFORE setting storyboard to prevent useEffect from interfering
      setIsSavedStoryboard(false)
      // Use setTimeout to ensure state update happens before storyboard is set
      setTimeout(() => {
        setStoryboard(response.data)
        if (onStoryboardGenerated) {
          onStoryboardGenerated(response.data)
        }
      }, 0)
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
      console.log('CreateStoryboard: Generating storyboard, setting isSavedStoryboard=false')
      setIsSavedStoryboard(false) // Ensure it's not marked as saved for new generation
      
      const payload = {
        script_content: scriptContent,
        llm_provider: llmProvider,
        hdr_enabled: hdrEnabled,
      }
      
      if (customParams) {
        payload.custom_params = customParams
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/generate-storyboard`, payload)

      console.log('CreateStoryboard: Storyboard generated (manual), explicitly setting isSavedStoryboard=false')
      console.log('CreateStoryboard: Response data:', response.data)
      // CRITICAL: Set to false and clear any loaded storyboard reference
      // Also ensure the response data doesn't have id/name that would make it look saved
      const storyboardData = { ...response.data }
      // Remove any id/name fields that might make it look like a saved storyboard
      delete storyboardData.id
      delete storyboardData.storyboard_id
      delete storyboardData.name
      
      setIsSavedStoryboard(false)
      setStoryboard(storyboardData)
      // Stay on step 2 to show generated storyboard
      if (onStoryboardGenerated) {
        onStoryboardGenerated(storyboardData)
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
      
      // Use existing frames if available (fast path), otherwise fallback to script
      const payload = storyboard && storyboard.frames && storyboard.frames.length > 0
        ? {
            frames: storyboard.frames.map(frame => ({
              scene_number: frame.scene_number,
              image: frame.image, // Already base64 encoded
              params: frame.params
            }))
          }
        : {
            script_content: scriptContent,
            llm_provider: llmProvider,
            hdr_enabled: hdrEnabled,
            custom_params: customParams,
          }
      
      const response = await axios.post(
        `${API_BASE_URL}/api/export-pdf`,
        payload,
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
    setIsSavedStoryboard(false)
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


        {/* Step 1: StoryBoard-Scripting */}
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
                Next: StoryBoard-Generation and Editing →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: StoryBoard-Generation and Editing */}
        {currentStep === 2 && (
          <div className="step-panel">
            {loading && !storyboard ? (
              <div className="generating-state">
                <div className="spinner"></div>
                <p>Generating storyboard from script...</p>
              </div>
            ) : storyboard ? (
              <>
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
                  isSavedStoryboard={isSavedStoryboard}
                />
                {/* Debug: Show current state */}
                {process.env.NODE_ENV === 'development' && (
                  <div style={{ padding: '10px', background: '#2a2a2a', marginTop: '10px', fontSize: '12px', color: '#888' }}>
                    Debug: isSavedStoryboard={String(isSavedStoryboard)}
                  </div>
                )}

                <div className="step-actions">
                  <button onClick={handlePrevious} className="previous-button">
                    ← Back to StoryBoard-Scripting
                  </button>
                  <button onClick={handleReset} className="reset-button">
                    🔄 Create New Storyboard
                  </button>
                </div>
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  )
}

export default CreateStoryboard

