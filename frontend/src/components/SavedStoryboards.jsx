import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Notification from './Notification'
import ConfirmModal from './ConfirmModal'
import './SavedStoryboards.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function SavedStoryboards({ onLoadStoryboard }) {
  const [savedStoryboards, setSavedStoryboards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [notification, setNotification] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState({ isOpen: false, storyboardId: null, storyboardName: null })

  useEffect(() => {
    loadSavedStoryboards()
  }, [])

  const loadSavedStoryboards = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/api/saved-storyboards`)
      setSavedStoryboards(response.data.storyboards || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      setSavedStoryboards([])
    } finally {
      setLoading(false)
    }
  }

  const handleLoadStoryboard = async (storyboardId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/saved-storyboard/${storyboardId}`)
      if (onLoadStoryboard) {
        onLoadStoryboard(response.data)
      }
    } catch (err) {
      setNotification({ message: 'Failed to load storyboard: ' + (err.response?.data?.detail || err.message), type: 'error' })
    }
  }

  const handleDeleteClick = (storyboardId, storyboardName, event) => {
    event.stopPropagation()
    setDeleteConfirm({
      isOpen: true,
      storyboardId,
      storyboardName
    })
  }

  const handleConfirmDelete = async () => {
    if (!deleteConfirm.storyboardId) return

    try {
      await axios.delete(`${API_BASE_URL}/api/saved-storyboard/${deleteConfirm.storyboardId}`)
      loadSavedStoryboards() // Reload list
      setNotification({ message: 'Storyboard deleted successfully!', type: 'success' })
      setDeleteConfirm({ isOpen: false, storyboardId: null, storyboardName: null })
    } catch (err) {
      setNotification({ message: 'Failed to delete storyboard: ' + (err.response?.data?.detail || err.message), type: 'error' })
      setDeleteConfirm({ isOpen: false, storyboardId: null, storyboardName: null })
    }
  }

  const handleCancelDelete = () => {
    setDeleteConfirm({ isOpen: false, storyboardId: null, storyboardName: null })
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
      <div className="saved-storyboards">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading saved storyboards...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="saved-storyboards">
        <div className="error-state">
          <p>Error: {error}</p>
          <button onClick={loadSavedStoryboards} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="saved-storyboards">
      <div className="saved-storyboards-header">
        <h2>My Storyboards</h2>
        <button onClick={loadSavedStoryboards} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {savedStoryboards.length === 0 ? (
        <div className="empty-state">
          <p>📭 No saved storyboards yet</p>
          <p className="empty-hint">Create a storyboard and save scenes to see them here</p>
        </div>
      ) : (
        <div className="storyboards-grid">
          {savedStoryboards.map((storyboard) => (
            <div
              key={storyboard.id}
              className="storyboard-card"
              onClick={() => handleLoadStoryboard(storyboard.id)}
            >
              <div className="storyboard-card-header">
                <h3>{storyboard.name || `Storyboard ${storyboard.id}`}</h3>
                <button
                  onClick={(e) => handleDeleteClick(storyboard.id, storyboard.name, e)}
                  className="delete-button"
                  title="Delete storyboard"
                >
                  🗑️
                </button>
              </div>

              {storyboard.thumbnail && (
                <div className="storyboard-thumbnail">
                  <img src={storyboard.thumbnail} alt="Thumbnail" />
                </div>
              )}

              <div className="storyboard-info">
                <div className="info-item">
                  <span className="info-label">Frames:</span>
                  <span className="info-value">{storyboard.frame_count || 0}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Created:</span>
                  <span className="info-value">{formatDate(storyboard.created_at)}</span>
                </div>
                {storyboard.updated_at && (
                  <div className="info-item">
                    <span className="info-label">Updated:</span>
                    <span className="info-value">{formatDate(storyboard.updated_at)}</span>
                  </div>
                )}
              </div>

              <div className="storyboard-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleLoadStoryboard(storyboard.id)
                  }}
                  className="load-button"
                >
                  📖 Load Storyboard
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

      <ConfirmModal
        isOpen={deleteConfirm.isOpen}
        title="Delete Storyboard"
        message={`Are you sure you want to delete "${deleteConfirm.storyboardName || 'this storyboard'}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmText="Delete"
        cancelText="Cancel"
        confirmButtonStyle="danger"
      />
    </div>
  )
}

export default SavedStoryboards

