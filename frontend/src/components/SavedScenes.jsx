import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Notification from './Notification'
import ConfirmModal from './ConfirmModal'
import ParameterCustomization from './ParameterCustomization'
import './SavedScenes.css'
import './StoryboardViewer.css'

// Use environment variable if set, otherwise use Render backend (production) or localhost (dev)
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://fibo-backend-jb9q.onrender.com')

function SavedScenes({ onLoadScene }) {
  const [savedScenes, setSavedScenes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [notification, setNotification] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState({ isOpen: false, sceneId: null, sceneDescription: null })
  const [editingScene, setEditingScene] = useState(null)
  const [editingParams, setEditingParams] = useState(null)
  const [regenerating, setRegenerating] = useState(false)

  useEffect(() => {
    loadSavedScenes()
  }, [])

  const loadSavedScenes = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/saved-scenes`)
      const scenes = response.data.scenes || []
      setSavedScenes(scenes)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      setSavedScenes([])
    } finally {
      setLoading(false)
    }
  }

  const handleEditScene = async (sceneId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/saved-scene/${sceneId}`)
      if (response.data.scene) {
        const scene = response.data.scene
        setEditingScene(scene)
        setEditingParams(scene.params || {})
      }
    } catch (err) {
      setNotification({ message: 'Failed to load scene: ' + (err.response?.data?.detail || err.message), type: 'error' })
    }
  }

  const handleCancelEdit = () => {
    setEditingScene(null)
    setEditingParams(null)
    setRegenerating(false)
  }

  const handleRegenerateScene = async (scene, newParams) => {
    if (!scene || !scene.description) {
      setNotification({ message: 'Scene description not found', type: 'error' })
      return
    }

    try {
      setRegenerating(true)
      
      const response = await axios.post(`${API_BASE_URL}/api/regenerate-scene`, {
        scene_number: scene.scene_number,
        scene_description: scene.description,
        params: newParams,
        script_content: ''
      })

      // Update the scene with new image
      const updatedScene = {
        ...scene,
        image: response.data.image,
        thumbnail: response.data.image,
        params: newParams
      }

      // Update the scene in the list
      setSavedScenes(prevScenes => 
        prevScenes.map(s => s.id === scene.id ? updatedScene : s)
      )

      // Update the editing scene
      setEditingScene(updatedScene)
      
      setNotification({ message: 'Scene regenerated successfully!', type: 'success' })
    } catch (error) {
      console.error('Failed to regenerate scene:', error)
      setNotification({ message: 'Failed to regenerate scene: ' + (error.response?.data?.detail || error.message), type: 'error' })
    } finally {
      setRegenerating(false)
    }
  }

  const handleDeleteClick = (sceneId, sceneDescription, event) => {
    event.stopPropagation()
    setDeleteConfirm({
      isOpen: true,
      sceneId,
      sceneDescription
    })
  }

  const handleConfirmDelete = async () => {
    if (!deleteConfirm.sceneId) return

    try {
      await axios.delete(`${API_BASE_URL}/api/saved-scene/${deleteConfirm.sceneId}`)
      loadSavedScenes() // Reload list
      setNotification({ message: 'Scene deleted successfully!', type: 'success' })
      setDeleteConfirm({ isOpen: false, sceneId: null, sceneDescription: null })
    } catch (err) {
      setNotification({ message: 'Failed to delete scene: ' + (err.response?.data?.detail || err.message), type: 'error' })
      setDeleteConfirm({ isOpen: false, sceneId: null, sceneDescription: null })
    }
  }

  const handleCancelDelete = () => {
    setDeleteConfirm({ isOpen: false, sceneId: null, sceneDescription: null })
  }

  const handleDownloadImage = (scene, event) => {
    event.stopPropagation()
    const link = document.createElement('a')
    link.href = scene.thumbnail
    link.download = `scene-${scene.scene_number}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="saved-scenes">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading saved scenes...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="saved-scenes">
        <div className="error-state">
          <p>Error: {error}</p>
          <button onClick={loadSavedScenes} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="saved-scenes">
      <div className="saved-scenes-header">
        <h2>My Scenes</h2>
        <button onClick={loadSavedScenes} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {savedScenes.length === 0 ? (
        <div className="empty-state">
          <p>📭 No saved scenes yet</p>
          <p className="empty-hint">Save scenes from storyboards to see them here</p>
        </div>
      ) : (
        <div className="scenes-grid">
          {savedScenes.map((scene) => {
            // Use name if provided and not empty, otherwise fallback to Scene number
            const sceneName = (scene.name && typeof scene.name === 'string' && scene.name.trim()) 
              ? scene.name.trim() 
              : `Scene ${scene.scene_number}`
            return (
            <div
              key={scene.id}
              className="scene-card"
            >
              {scene.thumbnail && (
                <div className="scene-image-container">
                  <img src={scene.thumbnail} alt={sceneName} />
                </div>
              )}
              
              <div className="scene-card-content">
                <div className="scene-header">
                  <span className="scene-title">{sceneName}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteClick(scene.id, scene.description || sceneName, e)
                    }}
                    className="delete-button"
                    title="Delete scene"
                  >
                    🗑️
                  </button>
                </div>

                {scene.description && (
                  <div className="scene-description">
                    <p>{scene.description}</p>
                  </div>
                )}

                <div className="scene-params">
                  <div className="param-labels-row">
                    <strong>Camera:</strong>
                    <strong>Lighting:</strong>
                    <strong>Color:</strong>
                  </div>
                  <div className="param-group-inline">
                    <div className="param-item-inline">
                      <span>Angle: {scene.params?.camera?.angle || 'N/A'}</span>
                      <span>FOV: {scene.params?.camera?.fov || 'N/A'}°</span>
                    </div>
                    <div className="param-item-inline">
                      <span>Time: {scene.params?.lighting?.time_of_day || 'N/A'}</span>
                      <span>Style: {scene.params?.lighting?.style || 'N/A'}</span>
                    </div>
                    <div className="param-item-inline">
                      <span>Palette: {scene.params?.color?.palette || 'N/A'}</span>
                      <span>Saturation: {scene.params?.color?.saturation?.toFixed ? scene.params.color.saturation.toFixed(2) : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div className="scene-meta">
                  <span className="meta-label">Saved:</span>
                  <span className="meta-value">{formatDate(scene.timestamp)}</span>
                </div>

                <div className="scene-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEditScene(scene.id)
                    }}
                    className="load-button"
                  >
                    ✏️ Edit Scene
                  </button>
                  <button
                    onClick={(e) => handleDownloadImage(scene, e)}
                    className="download-button"
                  >
                    ⬇️ Download
                  </button>
                </div>
              </div>
            </div>
            )
          })}
        </div>
      )}

      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      <ConfirmModal
        isOpen={deleteConfirm.isOpen}
        title="Delete Scene"
        message={`Are you sure you want to delete this scene? ${deleteConfirm.sceneDescription ? `"${deleteConfirm.sceneDescription.substring(0, 50)}${deleteConfirm.sceneDescription.length > 50 ? '...' : ''}"` : ''} This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonStyle="danger"
      />

      {/* Edit Scene Modal */}
      {editingScene && (
        <div className="edit-scene-modal">
          <div className="edit-scene-content">
            <div className="edit-scene-header">
              <h3>Edit Scene {editingScene.scene_number} {editingScene.name ? `- ${editingScene.name}` : ''}</h3>
              <button onClick={handleCancelEdit} className="close-edit-button">×</button>
            </div>
            
            <div className="edit-scene-body">
              <div className="edit-scene-layout">
                {/* Image Preview on Left */}
                <div className="edit-scene-image-preview">
                  <div className="preview-image-container">
                    <img
                      src={editingScene.thumbnail || editingScene.image}
                      alt={`Scene ${editingScene.scene_number}`}
                    />
                    {regenerating && (
                      <div className="preview-loading-overlay">
                        <div className="preview-spinner"></div>
                        <p>Regenerating scene...</p>
                      </div>
                    )}
                  </div>
                  {editingScene.description && (
                    <div className="preview-description">
                      <p>{editingScene.description}</p>
                    </div>
                  )}
                </div>

                {/* Options on Right */}
                <div className="edit-scene-options">
                  <p className="edit-description">Customize camera, lighting, color, and composition parameters for this scene.</p>
                  
                  <div className="edit-options-container">
                    <ParameterCustomization
                      params={editingParams || editingScene.params || {}}
                      onChange={setEditingParams}
                      onReset={() => setEditingParams(editingScene.params || {})}
                    />
                  </div>

                  <div className="edit-scene-actions">
                    <button onClick={handleCancelEdit} className="cancel-button">
                      Cancel
                    </button>
                    <button 
                      onClick={() => handleRegenerateScene(editingScene, editingParams || editingScene.params || {})}
                      disabled={regenerating}
                      className="apply-button"
                    >
                      {regenerating ? '⏳ Regenerating...' : '✨ Apply Changes'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SavedScenes

