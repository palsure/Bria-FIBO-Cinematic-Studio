import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Notification from './Notification'
import './SavedScenes.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function SavedScenes({ onLoadScene }) {
  const [savedScenes, setSavedScenes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    loadSavedScenes()
  }, [])

  const loadSavedScenes = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/saved-scenes`)
      setSavedScenes(response.data.scenes || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      setSavedScenes([])
    } finally {
      setLoading(false)
    }
  }

  const handleLoadScene = async (sceneId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/saved-scene/${sceneId}`)
      if (onLoadScene && response.data.scene) {
        onLoadScene(response.data.scene)
      }
    } catch (err) {
      setNotification({ message: 'Failed to load scene: ' + (err.response?.data?.detail || err.message), type: 'error' })
    }
  }

  const handleDeleteScene = async (sceneId, event) => {
    event.stopPropagation()
    if (!confirm('Are you sure you want to delete this scene?')) {
      return
    }

    try {
      await axios.delete(`${API_BASE_URL}/api/saved-scene/${sceneId}`)
      loadSavedScenes() // Reload list
      setNotification({ message: 'Scene deleted successfully!', type: 'success' })
    } catch (err) {
      setNotification({ message: 'Failed to delete scene: ' + (err.response?.data?.detail || err.message), type: 'error' })
    }
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
          {savedScenes.map((scene) => (
            <div
              key={scene.id}
              className="scene-card"
              onClick={() => handleLoadScene(scene.id)}
            >
              <div className="scene-card-header">
                <h3>Scene {scene.scene_number}</h3>
                <button
                  onClick={(e) => handleDeleteScene(scene.id, e)}
                  className="delete-button"
                  title="Delete scene"
                >
                  🗑️
                </button>
              </div>

              {scene.thumbnail && (
                <div className="scene-thumbnail">
                  <img src={scene.thumbnail} alt={`Scene ${scene.scene_number}`} />
                </div>
              )}

              {scene.description && (
                <div className="scene-description-preview">
                  <p>{scene.description.length > 100 ? scene.description.substring(0, 100) + '...' : scene.description}</p>
                </div>
              )}

              <div className="scene-info">
                <div className="info-item">
                  <span className="info-label">Camera:</span>
                  <span className="info-value">{scene.params?.camera?.angle || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Lighting:</span>
                  <span className="info-value">{scene.params?.lighting?.time_of_day || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Saved:</span>
                  <span className="info-value">{formatDate(scene.timestamp)}</span>
                </div>
              </div>

              <div className="scene-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleLoadScene(scene.id)
                  }}
                  className="load-button"
                >
                  📖 View Scene
                </button>
                <button
                  onClick={(e) => handleDownloadImage(scene, e)}
                  className="download-button"
                >
                  ⬇️ Download
                </button>
              </div>
            </div>
          ))}
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

export default SavedScenes

