import React from 'react'
import './ConfirmModal.css'

function ConfirmModal({ isOpen, title, message, onConfirm, onCancel, confirmText = 'OK', cancelText = 'Cancel', confirmButtonStyle = 'primary' }) {
  if (!isOpen) return null

  return (
    <div className="confirm-modal-overlay" onClick={onCancel}>
      <div className="confirm-modal-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="confirm-modal-title">{title || 'Confirm Action'}</h3>
        <p className="confirm-modal-message">{message}</p>
        <div className="confirm-modal-actions">
          <button
            onClick={onCancel}
            className="confirm-modal-button cancel-button"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`confirm-modal-button confirm-button ${confirmButtonStyle}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmModal

