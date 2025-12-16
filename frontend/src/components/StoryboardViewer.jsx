import React, { useState, useEffect } from 'react'
import axios from 'axios'
import ParameterCustomization from './ParameterCustomization'
import Notification from './Notification'
import './StoryboardViewer.css'

// Use environment variable if set, otherwise use relative path (for Vercel) or localhost (for dev)
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')

function StoryboardViewer({ storyboard, parsedScenes, onSaveStoryboard, onExportPDF, onExportAnimatic, exportLoading, onStoryboardUpdate, isSavedStoryboard = false }) {
  const [saving, setSaving] = useState({})
  const [saved, setSaved] = useState({})
  const [savingStoryboard, setSavingStoryboard] = useState(false)
  const [storyboardName, setStoryboardName] = useState('')
  const [savedStoryboardName, setSavedStoryboardName] = useState(null)
  const [savedStoryboardId, setSavedStoryboardId] = useState(null)
  const [editingStoryboardName, setEditingStoryboardName] = useState(false)
  const [editingFrame, setEditingFrame] = useState(null)
  const [editingParams, setEditingParams] = useState(null)
  const [regenerating, setRegenerating] = useState({})
  const [notification, setNotification] = useState(null)
  const [savingSceneModal, setSavingSceneModal] = useState({ isOpen: false, frameIndex: null, frame: null, sceneName: '' })

  // Initialize saved storyboard info if it's a saved storyboard
  useEffect(() => {
    console.log('StoryboardViewer useEffect: isSavedStoryboard=', isSavedStoryboard, 'storyboard exists?', !!storyboard)
    if (isSavedStoryboard === true && storyboard) {
      console.log('StoryboardViewer: Setting saved storyboard info')
      // Check if storyboard has name and id from saved data
      if (storyboard.name) {
        setSavedStoryboardName(storyboard.name)
      }
      if (storyboard.id || storyboard.storyboard_id) {
        setSavedStoryboardId(storyboard.id || storyboard.storyboard_id)
      }
    } else {
      // Clear saved name when it's a new storyboard (or undefined/false)
      console.log('StoryboardViewer: Clearing saved storyboard info (new storyboard)')
      setSavedStoryboardName(null)
      setSavedStoryboardId(null)
      setEditingStoryboardName(false)
    }
  }, [isSavedStoryboard, storyboard])

  if (!storyboard || !storyboard.frames) {
    return null
  }

  // Debug logging - ALWAYS log to help debug
  console.log('=== StoryboardViewer RENDER DEBUG ===')
  console.log('isSavedStoryboard:', isSavedStoryboard, 'type:', typeof isSavedStoryboard, '=== true?', isSavedStoryboard === true)
  console.log('savedStoryboardName:', savedStoryboardName)
  console.log('editingStoryboardName:', editingStoryboardName)
  console.log('storyboardName:', storyboardName)
  console.log('Will show save controls?', isSavedStoryboard !== true)
  console.log('Will show saved name?', isSavedStoryboard === true && savedStoryboardName)
  console.log('Condition check: isSavedStoryboard === true?', isSavedStoryboard === true)
  console.log('Will render save button in else branch?', isSavedStoryboard !== true)
  console.log('=====================================')

  // Helper function to get scene description
  const getSceneDescription = (sceneNumber) => {
    if (parsedScenes && Array.isArray(parsedScenes)) {
      const scene = parsedScenes.find(s => s.number === sceneNumber)
      return scene?.description || null
    }
    // Fallback: check if description is in frame params
    const frame = storyboard.frames.find(f => f.scene_number === sceneNumber)
    return frame?.params?.scene_description || null
  }

  const handleSaveSceneClick = (frame, index) => {
    // Open modal to get scene name
    setSavingSceneModal({
      isOpen: true,
      frameIndex: index,
      frame: frame,
      sceneName: ''
    })
  }

  const handleConfirmSaveScene = async () => {
    if (!savingSceneModal.frame || !savingSceneModal.sceneName.trim()) {
      setNotification({ message: 'Please enter a scene name', type: 'warning' })
      return
    }

    const { frame, frameIndex, sceneName } = savingSceneModal

    try {
      setSaving({ ...saving, [frameIndex]: true })
      
      const sceneDescription = getSceneDescription(frame.scene_number)
      
      const response = await axios.post(`${API_BASE_URL}/api/save-scene`, {
        scene_number: frame.scene_number,
        image: frame.image,
        params: frame.params,
        description: sceneDescription || sceneName.trim(),
        name: sceneName.trim(),
        timestamp: new Date().toISOString()
      })

      setSaved({ ...saved, [frameIndex]: true })
      setTimeout(() => {
        setSaved({ ...saved, [frameIndex]: false })
      }, 3000)
      setNotification({ message: 'Scene saved successfully!', type: 'success' })
      setSavingSceneModal({ isOpen: false, frameIndex: null, frame: null, sceneName: '' })
    } catch (error) {
      console.error('Failed to save scene:', error)
      setNotification({ message: 'Failed to save scene: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setSaving({ ...saving, [frameIndex]: false })
    }
  }

  const handleCancelSaveScene = () => {
    setSavingSceneModal({ isOpen: false, frameIndex: null, frame: null, sceneName: '' })
  }

  const handleDownloadImage = (frame, index) => {
    const link = document.createElement('a')
    link.href = frame.image
    link.download = `scene-${frame.scene_number}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleRegenerateScene = async (frameIndex, newParams) => {
    const frame = storyboard.frames[frameIndex]
    const sceneDescription = getSceneDescription(frame.scene_number)
    
    if (!sceneDescription) {
      setNotification({ message: 'Scene description not found', type: 'error' })
      return
    }

    try {
      setRegenerating({ ...regenerating, [frameIndex]: true })
      
      const response = await axios.post(`${API_BASE_URL}/api/regenerate-scene`, {
        scene_number: frame.scene_number,
        scene_description: sceneDescription,
        params: newParams,
        script_content: storyboard.script_content || ''
      })

      // Update the frame in the storyboard
      const updatedFrames = [...storyboard.frames]
      updatedFrames[frameIndex] = response.data
      
      const updatedStoryboard = {
        ...storyboard,
        frames: updatedFrames
      }

      // Update parent component
      if (onStoryboardUpdate) {
        onStoryboardUpdate(updatedStoryboard)
      }

      setEditingFrame(null)
      setEditingParams(null)
      setNotification({ message: 'Scene regenerated successfully!', type: 'success' })
    } catch (error) {
      setNotification({ message: 'Failed to regenerate scene: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setRegenerating({ ...regenerating, [frameIndex]: false })
    }
  }

  const handleCancelEdit = () => {
    setEditingFrame(null)
    setEditingParams(null)
  }

  const handleSaveStoryboard = async () => {
    if (!storyboardName.trim()) {
      setNotification({ message: 'Please enter a storyboard name', type: 'warning' })
      return
    }

    try {
      setSavingStoryboard(true)
      const response = await axios.post(`${API_BASE_URL}/api/save-storyboard`, {
        name: storyboardName.trim(),
        frames: storyboard.frames,
        script_content: null
      })

      setSavedStoryboardName(storyboardName.trim())
      setSavedStoryboardId(response.data.id || response.data.storyboard_id)
      setStoryboardName('')
      setNotification({ message: 'Storyboard saved successfully!', type: 'success' })
      if (onSaveStoryboard) {
        onSaveStoryboard(response.data)
      }
    } catch (error) {
      setNotification({ message: 'Failed to save storyboard: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setSavingStoryboard(false)
    }
  }

  const handleUpdateStoryboardName = async () => {
    if (!savedStoryboardId || !storyboardName.trim()) {
      setNotification({ message: 'Please enter a storyboard name', type: 'warning' })
      return
    }

    try {
      setSavingStoryboard(true)
      // Note: You may need to implement an update endpoint, or just save with new name
      const response = await axios.post(`${API_BASE_URL}/api/save-storyboard`, {
        name: storyboardName.trim(),
        frames: storyboard.frames,
        script_content: null
      })

      setSavedStoryboardName(storyboardName.trim())
      setSavedStoryboardId(response.data.id || response.data.storyboard_id)
      setEditingStoryboardName(false)
      setStoryboardName('')
      setNotification({ message: 'Storyboard name updated successfully!', type: 'success' })
    } catch (error) {
      setNotification({ message: 'Failed to update storyboard name: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setSavingStoryboard(false)
    }
  }

  const handleEditStoryboardName = () => {
    setStoryboardName(savedStoryboardName || '')
    setEditingStoryboardName(true)
  }

  const handleCancelEditName = () => {
    setEditingStoryboardName(false)
    setStoryboardName('')
  }

  return (
    <div className="storyboard-viewer">
      <div className="storyboard-header">
        <p className="storyboard-success-message">
          StoryBoard successfully generated with {storyboard.frame_count} {storyboard.frame_count === 1 ? 'scene' : 'scenes'}. Review and edit your generated scenes.
        </p>
        <div className="storyboard-actions-header">
          {/* ALWAYS show save controls unless explicitly a saved storyboard */}
          {isSavedStoryboard === true ? (
            // Show saved name for loaded saved storyboards ONLY
            savedStoryboardName && (
              <div className="saved-storyboard-info">
                <span className="saved-name-label">Saved as:</span>
                <span className="saved-name-value">{savedStoryboardName}</span>
              </div>
            )
          ) : (
            // For ALL other cases (new storyboards, undefined, false), show save/edit controls
            <>
              {/* If already saved (but not loaded from saved), show saved name with edit */}
              {savedStoryboardName && !editingStoryboardName ? (
                <div className="saved-storyboard-info">
                  <span className="saved-name-label">Saved as:</span>
                  <span className="saved-name-value">{savedStoryboardName}</span>
                  <button
                    onClick={handleEditStoryboardName}
                    className="edit-name-button"
                    title="Edit storyboard name"
                  >
                    ✏️ Edit
                  </button>
                </div>
              ) : editingStoryboardName ? (
                // Show edit controls when editing name
                <div className="save-storyboard-controls">
                  <input
                    type="text"
                    placeholder="Storyboard name..."
                    value={storyboardName}
                    onChange={(e) => setStoryboardName(e.target.value)}
                    className="storyboard-name-input"
                  />
                  <button
                    onClick={handleUpdateStoryboardName}
                    disabled={savingStoryboard || !storyboardName.trim()}
                    className="save-storyboard-button"
                  >
                    {savingStoryboard ? '⏳ Saving...' : '💾 Update'}
                  </button>
                  <button
                    onClick={handleCancelEditName}
                    className="cancel-edit-button"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                // DEFAULT: Show save controls for new/unsaved storyboards
                // This should ALWAYS render for new storyboards
                <div className="save-storyboard-controls" data-testid="save-storyboard-controls" style={{ display: 'flex', visibility: 'visible' }}>
                  <input
                    type="text"
                    placeholder="Storyboard name..."
                    value={storyboardName}
                    onChange={(e) => setStoryboardName(e.target.value)}
                    className="storyboard-name-input"
                    style={{ display: 'block', visibility: 'visible' }}
                  />
                  <button
                    onClick={handleSaveStoryboard}
                    disabled={savingStoryboard || !storyboardName.trim()}
                    className="save-storyboard-button"
                    data-testid="save-storyboard-button"
                    style={{ display: 'block', visibility: 'visible', opacity: (!storyboardName.trim() ? 0.6 : 1) }}
                  >
                    {savingStoryboard ? '⏳ Saving...' : '💾 Save Storyboard'}
                  </button>
                </div>
              )}
            </>
          )}
          
          {(onExportPDF || onExportAnimatic) && (
            <div className="export-buttons-inline">
              {onExportPDF && (
                <button onClick={onExportPDF} className="export-pdf-button" disabled={exportLoading}>
                  <span className="export-icon">📄</span>
                  <span className="export-text">Export PDF</span>
                </button>
              )}
              {onExportAnimatic && (
                <button onClick={onExportAnimatic} className="export-animatic-button" disabled={exportLoading}>
                  <span className="export-icon">🎬</span>
                  <span className="export-text">Export Animatic</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      
      <div className="frames-grid">
        {storyboard.frames.map((frame, index) => {
          const sceneDescription = getSceneDescription(frame.scene_number)
          return (
          <div key={index} className="frame-card">
            <div className="frame-image">
              <img
                src={frame.image}
                alt={`Scene ${frame.scene_number}`}
                loading="lazy"
              />
            </div>
            
            <div className="frame-card-content">
              <div className="frame-header">
                <span className="scene-number">Scene {frame.scene_number}</span>
              </div>
              
              {sceneDescription && (
                <div className="scene-description">
                  <p>{sceneDescription}</p>
                </div>
              )}
              
              <div className="frame-params">
                <div className="param-labels-row">
                  <strong>Camera:</strong>
                  <strong>Lighting:</strong>
                  <strong>Color:</strong>
                </div>
                <div className="param-group-inline">
                  <div className="param-item-inline">
                    <span>Angle: {frame.params.camera?.angle || 'N/A'}</span>
                    <span>FOV: {frame.params.camera?.fov || 'N/A'}°</span>
                  </div>
                  <div className="param-item-inline">
                    <span>Time: {frame.params.lighting?.time_of_day || 'N/A'}</span>
                    <span>Style: {frame.params.lighting?.style || 'N/A'}</span>
                  </div>
                  <div className="param-item-inline">
                    <span>Palette: {frame.params.color?.palette || 'N/A'}</span>
                    <span>Saturation: {frame.params.color?.saturation?.toFixed(2) || 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div className="frame-actions">
              <button
                onClick={() => {
                  setEditingFrame(index)
                  setEditingParams(frame.params)
                }}
                className="edit-button"
                title="Edit scene parameters"
              >
                ✏️ Edit Scene
              </button>
              <button
                onClick={() => handleSaveSceneClick(frame, index)}
                disabled={saving[index]}
                className={`save-button ${saved[index] ? 'saved' : ''}`}
                title="Save scene to library"
              >
                {saving[index] ? '⏳ Saving...' : saved[index] ? '✓ Saved!' : '💾 Save Scene'}
              </button>
              <button
                onClick={() => handleDownloadImage(frame, index)}
                className="download-button"
                title="Download image"
              >
                ⬇️ Download
              </button>
              </div>
            </div>
          </div>
          )
        })}
      </div>

      {/* Edit Scene Modal */}
      {editingFrame !== null && (
        <div className="edit-scene-modal">
          <div className="edit-scene-content">
            <div className="edit-scene-header">
              <h3>Edit Scene {storyboard.frames[editingFrame]?.scene_number}</h3>
              <button onClick={handleCancelEdit} className="close-edit-button">×</button>
            </div>
            
            <div className="edit-scene-body">
              <div className="edit-scene-layout">
                {/* Image Preview on Left */}
                <div className="edit-scene-image-preview">
                  <div className="preview-image-container">
                    <img
                      src={storyboard.frames[editingFrame]?.image}
                      alt={`Scene ${storyboard.frames[editingFrame]?.scene_number}`}
                    />
                    {regenerating[editingFrame] && (
                      <div className="preview-loading-overlay">
                        <div className="preview-spinner"></div>
                        <p>Regenerating scene...</p>
                      </div>
                    )}
                  </div>
                  {getSceneDescription(storyboard.frames[editingFrame]?.scene_number) && (
                    <div className="preview-description">
                      <p>{getSceneDescription(storyboard.frames[editingFrame]?.scene_number)}</p>
                    </div>
                  )}
                </div>

                {/* Options on Right */}
                <div className="edit-scene-options">
                  <p className="edit-description">Customize camera, lighting, color, and composition parameters for this scene.</p>
                  
                  <div className="edit-options-container">
                    <ParameterCustomization
                      params={editingParams || storyboard.frames[editingFrame]?.params}
                      onChange={setEditingParams}
                      onReset={() => setEditingParams(storyboard.frames[editingFrame]?.params)}
                    />
                  </div>

                  <div className="edit-scene-actions">
                    <button onClick={handleCancelEdit} className="cancel-button">
                      Cancel
                    </button>
                    <button 
                      onClick={() => handleRegenerateScene(editingFrame, editingParams || storyboard.frames[editingFrame]?.params)}
                      disabled={regenerating[editingFrame]}
                      className="apply-button"
                    >
                      {regenerating[editingFrame] ? '⏳ Regenerating...' : '✨ Apply Changes'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save Scene Modal */}
      {savingSceneModal.isOpen && (
        <div className="save-scene-modal-overlay" onClick={handleCancelSaveScene}>
          <div className="save-scene-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="save-scene-modal-header">
              <h3>Save Scene {savingSceneModal.frame?.scene_number}</h3>
              <button onClick={handleCancelSaveScene} className="close-save-scene-button">×</button>
            </div>
            <div className="save-scene-modal-body">
              <p className="save-scene-modal-description">
                {getSceneDescription(savingSceneModal.frame?.scene_number) || 'Enter a name for this scene'}
              </p>
              <input
                type="text"
                placeholder="Scene name..."
                value={savingSceneModal.sceneName}
                onChange={(e) => setSavingSceneModal({ ...savingSceneModal, sceneName: e.target.value })}
                className="save-scene-name-input"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && savingSceneModal.sceneName.trim()) {
                    handleConfirmSaveScene()
                  } else if (e.key === 'Escape') {
                    handleCancelSaveScene()
                  }
                }}
              />
            </div>
            <div className="save-scene-modal-actions">
              <button
                onClick={handleCancelSaveScene}
                className="save-scene-cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSaveScene}
                disabled={!savingSceneModal.sceneName.trim() || saving[savingSceneModal.frameIndex]}
                className="save-scene-confirm-button"
              >
                {saving[savingSceneModal.frameIndex] ? '⏳ Saving...' : '💾 Save Scene'}
              </button>
            </div>
          </div>
        </div>
      )}

      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  )
}

export default StoryboardViewer




