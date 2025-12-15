# Quick Start Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- BRIA API Key

## Installation

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env and add: BRIA_API_TOKEN=your_key_here
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## Running

### Terminal 1 - Backend
```bash
cd backend
KMP_DUPLICATE_LIB_OK=TRUE python main.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Usage

1. Open `http://localhost:5173` (or the port shown in terminal)
2. Go to "Create Storyboard" tab
3. Paste or upload your script
4. Wait for automatic generation
5. Edit scenes as needed
6. Save and export!

