import React, { useState } from 'react'
import axios from 'axios'
import ParameterCustomization from './ParameterCustomization'
import Notification from './Notification'
import './StoryboardViewer.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function StoryboardViewer({ storyboard, parsedScenes, onSaveStoryboard, onExportPDF, onExportAnimatic, exportLoading, onStoryboardUpdate }) {
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

  if (!storyboard || !storyboard.frames) {
    return null
  }

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

  const handleSaveScene = async (frame, index) => {
    try {
      setSaving({ ...saving, [index]: true })
      
      const sceneDescription = getSceneDescription(frame.scene_number)
      
      const response = await axios.post(`${API_BASE_URL}/api/save-scene`, {
        scene_number: frame.scene_number,
        image: frame.image,
        params: frame.params,
        description: sceneDescription,
        timestamp: new Date().toISOString()
      })

      setSaved({ ...saved, [index]: true })
      setTimeout(() => {
        setSaved({ ...saved, [index]: false })
      }, 3000)
      setNotification({ message: 'Scene saved successfully!', type: 'success' })
    } catch (error) {
      console.error('Failed to save scene:', error)
      setNotification({ message: 'Failed to save scene: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setSaving({ ...saving, [index]: false })
    }
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
        <h2>Storyboard ({storyboard.frame_count} frames)</h2>
        <div className="storyboard-actions-header">
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
          ) : (
            <div className="save-storyboard-controls">
              <input
                type="text"
                placeholder="Storyboard name..."
                value={storyboardName}
                onChange={(e) => setStoryboardName(e.target.value)}
                className="storyboard-name-input"
              />
              {editingStoryboardName ? (
                <>
                  <button
                    onClick={handleUpdateStoryboardName}
                    disabled={savingStoryboard}
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
                </>
              ) : (
                <button
                  onClick={handleSaveStoryboard}
                  disabled={savingStoryboard}
                  className="save-storyboard-button"
                >
                  {savingStoryboard ? '⏳ Saving...' : '💾 Save Storyboard'}
                </button>
              )}
            </div>
          )}
        </div>
        
        {(onExportPDF || onExportAnimatic) && (
          <div className="export-section">
            <div className="export-buttons-container">
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
          </div>
        )}
      </div>
      
      <div className="frames-grid">
        {storyboard.frames.map((frame, index) => {
          const sceneDescription = getSceneDescription(frame.scene_number)
          return (
          <div key={index} className="frame-card">
            <div className="frame-header">
              <span className="scene-number">Scene {frame.scene_number}</span>
            </div>
            
            {sceneDescription && (
              <div className="scene-description">
                <p>{sceneDescription}</p>
              </div>
            )}
            
            <div className="frame-image">
              <img
                src={frame.image}
                alt={`Scene ${frame.scene_number}`}
                loading="lazy"
              />
            </div>
            
            <div className="frame-params">
              <div className="param-group-inline">
                <div className="param-item-inline">
                  <strong>Camera:</strong>
                  <span>Angle: {frame.params.camera?.angle || 'N/A'}</span>
                  <span>FOV: {frame.params.camera?.fov || 'N/A'}°</span>
                </div>
                <div className="param-item-inline">
                  <strong>Lighting:</strong>
                  <span>Time: {frame.params.lighting?.time_of_day || 'N/A'}</span>
                  <span>Style: {frame.params.lighting?.style || 'N/A'}</span>
                </div>
                <div className="param-item-inline">
                  <strong>Color:</strong>
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
                onClick={() => handleSaveScene(frame, index)}
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
              <p className="edit-description">Customize camera, lighting, color, and composition parameters for this scene.</p>
              
              <ParameterCustomization
                params={editingParams || storyboard.frames[editingFrame]?.params}
                onChange={setEditingParams}
                onReset={() => setEditingParams(storyboard.frames[editingFrame]?.params)}
              />

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




