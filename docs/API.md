# API Documentation

## Base URL

`http://localhost:8000/api`

## Storyboard Generation

### Parse Script
```
POST /api/parse-script
Content-Type: application/json

{
  "content": "script text here"
}
```

### Upload Script File
```
POST /api/upload-script
Content-Type: multipart/form-data

file: <file>
```

### Generate Storyboard
```
POST /api/generate-storyboard
Content-Type: application/json

{
  "script_content": "script text",
  "custom_params": {
    "camera": {...},
    "lighting": {...},
    "color": {...}
  }
}
```

## Storyboard Management

### Save Storyboard
```
POST /api/save-storyboard
Content-Type: application/json

{
  "name": "My Storyboard",
  "frames": [...],
  "script_content": "..."
}
```

### List Storyboards
```
GET /api/saved-storyboards
```

### Get Storyboard
```
GET /api/saved-storyboard/{id}
```

### Delete Storyboard
```
DELETE /api/saved-storyboard/{id}
```

## Scene Management

### Save Scene
```
POST /api/save-scene
Content-Type: application/json

{
  "scene_number": 1,
  "image": "data:image/png;base64,...",
  "params": {...},
  "description": "..."
}
```

### List Scenes
```
GET /api/saved-scenes
```

### Get Scene
```
GET /api/saved-scene/{id}
```

### Delete Scene
```
DELETE /api/saved-scene/{id}
```

## Scene Editing

### Regenerate Scene
```
POST /api/regenerate-scene
Content-Type: application/json

{
  "scene_number": 1,
  "scene_description": "...",
  "params": {...}
}
```

## Export

### Export PDF
```
POST /api/export-pdf
Content-Type: application/json

{
  "script_content": "...",
  "custom_params": {...}
}
```

### Export Animatic
```
POST /api/export-animatic
Content-Type: application/json

{
  "script_content": "...",
  "custom_params": {...}
}
```

