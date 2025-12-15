import React, { useState } from 'react'
import CreateStoryboard from './components/CreateStoryboard'
import SavedStoryboards from './components/SavedStoryboards'
import SavedScenes from './components/SavedScenes'
import UsageGuide from './components/UsageGuide'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('create')
  const [storyboard, setStoryboard] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showGuide, setShowGuide] = useState(false)

  const handleStoryboardGenerated = (storyboardData) => {
    setStoryboard(storyboardData)
    setError(null)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setStoryboard(null)
  }

  const handleLoading = (isLoading) => {
    setLoading(isLoading)
  }

  const handleLoadStoryboard = (storyboardData) => {
    setStoryboard(storyboardData)
    setError(null)
    setActiveTab('create') // Switch to create tab to view the loaded storyboard
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎬 FIBO Studio</h1>
          <button
            className="help-button"
            onClick={() => setShowGuide(true)}
            aria-label="Open Usage Guide"
            title="Usage Guide"
          >
            ❓ Guide
          </button>
        </div>
        <p>AI-Powered Cinematic Pre-Visualization Pipeline. Powered by Bria FIBO and JSON-Native Visual Generation</p>
      </header>

      <div className="app-tabs">
        <button
          className={`tab-button ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          ✨ Create Storyboard
        </button>
        <button
          className={`tab-button ${activeTab === 'saved' ? 'active' : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          📚 My Storyboards
        </button>
        <button
          className={`tab-button ${activeTab === 'scenes' ? 'active' : ''}`}
          onClick={() => setActiveTab('scenes')}
        >
          🎬 My Scenes
        </button>
      </div>

      <main className="app-main">
        {activeTab === 'create' && (
          <CreateStoryboard
            loadedStoryboard={storyboard}
            onStoryboardGenerated={handleStoryboardGenerated}
            onError={handleError}
            onLoading={handleLoading}
          />
        )}

        {activeTab === 'saved' && (
          <SavedStoryboards onLoadStoryboard={handleLoadStoryboard} />
        )}

        {activeTab === 'scenes' && (
          <SavedScenes onLoadScene={(scene) => {
            // Could navigate to create tab and show scene, or just show in a modal
            console.log('Scene loaded:', scene)
          }} />
        )}
      </main>

      <UsageGuide
        isOpen={showGuide}
        onClose={() => setShowGuide(false)}
      />
    </div>
  )
}

export default App




