# FIBO Studio Frontend

React-based frontend for FIBO Studio - AI-Powered Cinematic Pre-Visualization Pipeline.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to the backend at `http://localhost:8000`.

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Features

- Script upload (file or text input)
- Real-time storyboard generation
- Interactive storyboard viewer
- PDF and animatic export
- Parameter visualization
- Responsive design

## Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ScriptUpload.jsx      # Script input component
│   │   └── StoryboardViewer.jsx   # Storyboard display
│   ├── App.jsx                    # Main app component
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles
├── index.html
├── package.json
└── vite.config.js
```





