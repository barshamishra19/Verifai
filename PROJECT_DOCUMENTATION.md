# 🎬 VERIFAI - Project Documentation
**VERIFy AI-generated videos**  
*"See Exactly Why. Detect Frame-by-Frame. Trust the Evidence."*

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Current Implementation Status](#current-implementation-status)
3. [Architecture](#architecture)
4. [What's Implemented](#whats-implemented)
5. [What's Left to Implement](#whats-left-to-implement)
6. [Future Enhancements](#future-enhancements)
7. [Installation & Setup](#installation--setup)
8. [API Reference](#api-reference)
9. [Known Issues](#known-issues)

---

## 🎯 Project Overview

**VERIFAI** is a multimodal AI video detection system designed to identify AI-generated videos using multiple detection engines. The system combines spatial artifact detection, temporal consistency analysis, forensic frequency analysis, and metadata verification to provide accurate classification with explainable results.

### Key Features
- ✅ **Multi-Engine Detection**: 4 parallel detection engines for comprehensive analysis
- ✅ **Browser Extension**: Chrome extension for one-click video verification
- ✅ **FastAPI Backend**: High-performance REST API for video analysis
- ✅ **Explainable AI**: Provides evidence-based reasoning for each classification
- ✅ **Database Storage**: SQLite database for analysis history

---

## 📊 Current Implementation Status

### Overall Progress: **~60% Complete**

| Component | Status | Completion |
|-----------|--------|------------|
| **Backend API** | ✅ Implemented | 80% |
| **Spatial Detection** | ✅ Working | 100% |
| **Temporal Detection** | ⚠️ Partial | 60% |
| **Forensic Detection** | ✅ Working | 90% |
| **Metadata Detection** | ⚠️ Basic | 40% |
| **Browser Extension** | ✅ Working | 70% |
| **Database** | ✅ Working | 100% |
| **Reasoning Engine** | ⚠️ Basic | 50% |
| **ONNX Deployment** | ❌ Not Started | 0% |
| **Advanced Features** | ❌ Not Started | 0% |

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFAI SYSTEM                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Chrome Extension │────────▶│  FastAPI Backend │         │
│  │  (popup.js)       │  HTTP   │  (pipeline.py)   │         │
│  └──────────────────┘         └──────────────────┘         │
│                                         │                    │
│                        ┌────────────────┼────────────────┐  │
│                        │                │                │  │
│              ┌─────────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
│              │ Spatial Engine │  │  Temporal  │  │  Forensic   │
│              │  (SigLIP CNN)  │  │   Engine   │  │   Engine    │
│              │   94% Acc.     │  │  (Motion)  │  │   (FFT)     │
│              └────────────────┘  └────────────┘  └─────────────┘
│                        │                │                │  │
│                        └────────────────┴────────────────┘  │
│                                         │                    │
│                          ┌──────────────▼────────────────┐  │
│                          │    Ensemble Decision          │  │
│                          │    (Weighted Average)         │  │
│                          └──────────────┬────────────────┘  │
│                                         │                    │
│                          ┌──────────────▼────────────────┐  │
│                          │    Reasoning Engine           │  │
│                          │    (Evidence Generation)      │  │
│                          └──────────────┬────────────────┘  │
│                                         │                    │
│                          ┌──────────────▼────────────────┐  │
│                          │    SQLite Database            │  │
│                          │    (Analysis History)         │  │
│                          └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ What's Implemented

### 1. **Backend API (80% Complete)**

#### Files:
- [`backend/pipeline.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/pipeline.py) - Main FastAPI application

#### Features:
✅ **Two Analysis Endpoints**:
- `POST /api/analyze` - Upload and analyze video files
- `POST /api/analyze_url` - Analyze videos from URLs

✅ **Core Processing Pipeline**:
- Frame extraction from videos
- Multi-engine parallel processing
- Ensemble scoring with weighted average
- Evidence generation
- Error handling with NaN protection
- Temporary file cleanup

✅ **Ensemble Formula**:
```python
final_score = (
    spatial_score × 0.30 +
    temporal_score × 0.35 +
    forensic_score × 0.25 +
    metadata_score × 0.10
)
```

#### What Works:
- ✅ Video upload and URL download
- ✅ Frame extraction (using OpenCV)
- ✅ Multi-engine detection
- ✅ JSON response generation
- ✅ Database logging
- ✅ Error handling

#### Limitations:
- ⚠️ URL download only works for direct video links (not YouTube/TikTok)
- ⚠️ No streaming support
- ⚠️ No batch processing

---

### 2. **Spatial Detection Engine (100% Complete)**

#### File:
- [`backend/models/spatial_detector.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/models/spatial_detector.py)

#### Implementation:
✅ **Model**: `prithivMLmods/deepfake-detector-model-v1` (SigLIP-based)
- Pre-trained on 20K real/fake images
- 94.44% accuracy
- ~200MB model size

✅ **Detection Process**:
1. BGR to RGB conversion
2. Image preprocessing (224×224)
3. CNN inference
4. Softmax probability calculation
5. Returns fake confidence score (0-1)

✅ **Hardware Support**:
- CUDA acceleration (if available)
- CPU fallback

#### Performance:
- **Inference Time**: 50-100ms per frame (GPU) / 200-300ms (CPU)
- **Accuracy**: 94.44%

---

### 3. **Temporal Detection Engine (60% Complete)**

#### File:
- [`backend/models/temporal_detector.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/models/temporal_detector.py)

#### What's Implemented:
✅ **Motion Smoothness Detection**:
- Optical flow analysis using Farneback method
- Detects unnaturally smooth motion (AI characteristic)
- Variance-based scoring

✅ **Features**:
- Frame-to-frame optical flow computation
- Motion magnitude calculation
- Smoothness score (high = AI-like)

#### What's Missing:
❌ **Lip-Sync Error Detection** (code exists but not integrated)
❌ **Blink Pattern Analysis** (code exists but not integrated)
❌ **LSTM Model** (architecture defined but not trained)
❌ **Temporal sequence analysis** (currently only motion smoothness)

#### Current Behavior:
- Only `detect_motion_smoothness()` is called in pipeline
- Other methods exist but not used

---

### 4. **Forensic Detection Engine (90% Complete)**

#### File:
- [`backend/models/forensic_detector.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/models/forensic_detector.py)

#### Implementation:
✅ **Frequency Domain Analysis**:
- Fast Fourier Transform (FFT) on grayscale frames
- High-frequency energy detection
- GAN/Diffusion artifact identification

✅ **Detection Method**:
1. Convert frame to grayscale
2. Apply 2D FFT
3. Mask low frequencies (center)
4. Calculate high-frequency ratio
5. Score using empirical formula: `max(0, (ratio - 0.5) × 3)`

✅ **Tuned for Real vs AI**:
- Real videos: ~0.62 ratio → 0.36 score
- AI videos: ~0.82 ratio → 0.96 score

#### What's Missing:
❌ **GAN-specific detection** (partially implemented but not integrated)
❌ **Diffusion model fingerprint detection**
❌ **Compression anomaly detection**

---

### 5. **Metadata Detection Engine (40% Complete)**

#### File:
- [`backend/models/metadata_detector.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/models/metadata_detector.py)

#### Current Status:
⚠️ **Stub Implementation** - Returns placeholder values

#### What's Missing:
❌ C2PA credential parsing
❌ EXIF metadata analysis
❌ SynthID watermark detection
❌ Video codec/encoding metadata extraction

---

### 6. **Browser Extension (70% Complete)**

#### Files:
- [`extension/manifest.json`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/extension/manifest.json)
- [`extension/popup.html`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/extension/popup.html)
- [`extension/popup.js`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/extension/popup.js)
- [`extension/style.css`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/extension/style.css)

#### Features:
✅ **Two Analysis Modes**:
1. **Upload Mode**: User manually uploads video file
2. **Scan Mode**: Detects video on current webpage

✅ **UI Components**:
- File upload drag-and-drop zone
- Loading spinner
- Results display (verdict badge + confidence %)
- Evidence list
- Reset functionality

✅ **Integration**:
- Connects to `http://localhost:8000` backend
- Uses Chrome scripting API to inject page scripts
- Extracts video URLs from DOM

#### What Works:
- ✅ File upload to backend
- ✅ Page video detection (finds `<video>` tags)
- ✅ Results visualization
- ✅ Error handling

#### Limitations:
- ⚠️ Only works with direct `<video>` elements (not iframe videos like YouTube)
- ⚠️ Requires backend to be running on localhost:8000
- ⚠️ No HTTPS support
- ⚠️ No authentication

---

### 7. **Database System (100% Complete)**

#### File:
- [`backend/database.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/database.py)

#### Implementation:
✅ **SQLite Database** (`verifai_results.db`)

✅ **Schema**:
```sql
CREATE TABLE analysis_results (
    job_id TEXT PRIMARY KEY,
    filename TEXT,
    classification TEXT,
    confidence REAL,
    spatial_score REAL,
    temporal_score REAL,
    forensic_score REAL,
    metadata_score REAL,
    timestamp DATETIME
)
```

✅ **Functions**:
- `init_db()` - Create tables on startup
- `save_analysis_result()` - Store analysis results

#### What Works:
- ✅ Automatic database initialization
- ✅ Result logging with all engine scores
- ✅ Timestamp tracking

#### What's Missing:
❌ Query/retrieval endpoints
❌ History viewing in extension
❌ Result export functionality
❌ Analytics/statistics

---

### 8. **Utility Modules**

#### [`backend/utils/video_processor.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/utils/video_processor.py)
✅ Frame extraction using OpenCV
✅ Returns list of numpy arrays (BGR format)

#### [`backend/utils/reasoning_engine.py`](file:///c:/Users/barsha%20mishra/Desktop/myprojects/verifai-project/backend/utils/reasoning_engine.py)
⚠️ **Basic Implementation**:
- Simple threshold-based evidence generation
- Returns list of evidence objects
- Limited to 3 evidence types

---

## ❌ What's Left to Implement

### High Priority

#### 1. **LSTM Temporal Model Training**
**Status**: ❌ Not Started  
**Files Needed**: 
- `backend/models/temporal_detector.py` (extend existing)
- Training script
- Dataset preparation

**Requirements**:
- Train LSTM on FaceForensics++ dataset
- Implement lip-sync error detection
- Add blink pattern analysis
- Integrate into main pipeline

**Estimated Effort**: 2-3 weeks

---

#### 2. **Metadata Detection Implementation**
**Status**: ❌ Not Started  
**File**: `backend/models/metadata_detector.py`

**Required Features**:
- C2PA credential parsing
- EXIF metadata extraction
- SynthID watermark detection
- Video codec analysis

**Libraries Needed**:
```python
pip install c2pa-python exifread pymediainfo
```

**Estimated Effort**: 1 week

---

#### 3. **Enhanced Reasoning Engine**
**Status**: ❌ Not Started  
**File**: `backend/utils/reasoning_engine.py`

**Current vs Required**:

| Current | Required |
|---------|----------|
| 3 evidence types | 10+ evidence types |
| Simple thresholds | Confidence-based ranking |
| No frame grounding | Frame-level evidence |
| Static messages | Dynamic explanations |

**Estimated Effort**: 1 week

---

#### 4. **YouTube/Social Media Support**
**Status**: ❌ Not Started  
**File**: `backend/pipeline.py`

**Implementation**:
```python
# Add yt-dlp integration
pip install yt-dlp

def download_video_ytdlp(url):
    import yt_dlp
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'temp_%(id)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
```

**Platforms to Support**:
- YouTube
- YouTube Shorts
- TikTok
- Instagram Reels
- Twitter/X videos

**Estimated Effort**: 3-5 days

---

### Medium Priority

#### 5. **ONNX Browser Deployment**
**Status**: ❌ Not Started

**Requirements**:
- Export SigLIP model to ONNX format
- Integrate ONNX.js in extension
- Implement client-side inference
- Add fallback to backend

**Benefits**:
- Faster analysis (no network latency)
- Privacy (no video upload)
- Offline capability

**Estimated Effort**: 1-2 weeks

---

#### 6. **Advanced Forensic Detection**
**Status**: ❌ Partial

**Missing Features**:
- GAN block artifact detection (code exists but not integrated)
- Diffusion model fingerprinting
- Color banding analysis
- Compression pattern analysis

**File**: Extend `backend/models/forensic_detector.py`

**Estimated Effort**: 1 week

---

#### 7. **Result History & Analytics**
**Status**: ❌ Not Started

**Required Endpoints**:
```python
GET /api/history?limit=50
GET /api/statistics
GET /api/export/{job_id}
DELETE /api/clear_history
```

**Extension Features**:
- History tab in popup
- Export results as PDF/JSON
- Statistics dashboard

**Estimated Effort**: 1 week

---

#### 8. **Authentication & User Management**
**Status**: ❌ Not Started

**Features**:
- User accounts
- API keys
- Rate limiting
- Tiered access (Free/Pro)

**Estimated Effort**: 2 weeks

---

### Low Priority

#### 9. **Batch Processing**
**Status**: ❌ Not Started

**Feature**: Upload multiple videos for analysis

**Endpoint**:
```python
POST /api/batch_analyze
```

**Estimated Effort**: 3-5 days

---

#### 10. **Heatmap Generation**
**Status**: ❌ Not Started

**Feature**: Generate visual heatmaps showing artifact locations

**Implementation**:
- Use Grad-CAM for spatial artifacts
- Overlay heatmaps on frames
- Return as image/video

**Estimated Effort**: 1 week

---

## 🚀 Future Enhancements

### Advanced Features (Not in Current Scope)

#### 1. **Real-Time Streaming Analysis**
- Analyze live video streams
- WebRTC integration
- Frame-by-frame processing

#### 2. **Mobile App**
- React Native extension
- iOS/Android support
- Camera integration

#### 3. **API Marketplace**
- Public API for developers
- Webhook notifications
- Third-party integrations

#### 4. **Advanced AI Models**

##### Multi-Modal Analysis:
- Audio deepfake detection (using Wav2Vec 2.0)
- Speech-video sync verification
- Background consistency checking

##### State-of-the-Art Models:
- Replace SigLIP with Vision Transformer (ViT)
- Add CLIP for semantic analysis
- Implement Attention-based LSTM

#### 5. **Cloud Deployment**
- AWS/GCP deployment
- Scalable architecture
- CDN for model weights

#### 6. **Browser Support**
- Firefox extension
- Safari extension
- Edge extension

#### 7. **Advanced Forensics**
- GAN fingerprinting database
- Generator model identification
- Watermark embedding

#### 8. **Explainability Dashboard**
- Interactive evidence viewer
- Frame-by-frame playback
- Detailed confidence graphs

#### 9. **Collaborative Features**
- Share analysis results
- Community voting
- False positive reporting

#### 10. **Integration Features**
- Slack/Discord bots
- Twitter bot for public verification
- API webhooks

---

## 🛠️ Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# pip
pip --version
```

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run backend server
python pipeline.py
```

**Backend will start on**: `http://localhost:8000`

### Extension Setup

```bash
# 1. Open Chrome
# 2. Navigate to: chrome://extensions/
# 3. Enable "Developer mode" (top-right toggle)
# 4. Click "Load unpacked"
# 5. Select the extension/ folder
```

### Testing

```bash
# 1. Start backend
cd backend
python pipeline.py

# 2. Open Chrome extension
# 3. Upload a video or scan a webpage with video
```

---

## 📡 API Reference

### Endpoints

#### 1. Analyze Video File
```http
POST /api/analyze
Content-Type: multipart/form-data

Body: 
  file: <video_file>
```

**Response**:
```json
{
  "job_id": "uuid",
  "final_confidence": 0.85,
  "classification": "AI-Generated",
  "evidence": [
    {
      "type": "Spatial",
      "explanation": "Detected distortions in skin texture/hand geometry."
    },
    {
      "type": "Temporal",
      "explanation": "Movement is unnaturally smooth (Characteristic of AI)."
    }
  ],
  "processing_time_ms": 8450.23
}
```

---

#### 2. Analyze Video URL
```http
POST /api/analyze_url
Content-Type: application/json

Body:
{
  "url": "https://example.com/video.mp4"
}
```

**Response**: Same as above

---

#### Error Responses

```json
{
  "detail": "Failed to download video. Link might be private or blocked."
}
```

```json
{
  "detail": "Could not process video frames. The file might be corrupted or not a valid video."
}
```

---

## 🐛 Known Issues

### 1. **False Positives on Real Content**
**Description**: System sometimes flags real videos as AI-generated  
**Cause**: Forensic detector threshold needs tuning  
**Status**: ⚠️ Partially Fixed (reduced scaling factor from 20 to 3)  
**Workaround**: Adjust `forensic_score` threshold

### 2. **YouTube Video Support**
**Description**: Cannot download YouTube videos  
**Cause**: Uses `requests` library instead of `yt-dlp`  
**Status**: ❌ Not Fixed  
**Workaround**: Use direct video links only

### 3. **Browser Extension CORS**
**Description**: CORS errors when backend not on localhost  
**Cause**: No CORS headers configured  
**Status**: ❌ Not Fixed  
**Workaround**: Run backend on localhost:8000

### 4. **Temporal Detection Incomplete**
**Description**: Only motion smoothness is checked  
**Cause**: Lip-sync and blink detection not integrated  
**Status**: ⚠️ Partial Implementation  
**Workaround**: Lower temporal weight in ensemble

### 5. **Metadata Detection Non-Functional**
**Description**: Always returns placeholder values  
**Cause**: Stub implementation  
**Status**: ❌ Not Implemented  
**Workaround**: Set metadata weight to 0.0 in ensemble

### 6. **No Result History**
**Description**: Cannot view past analyses in extension  
**Cause**: No history API endpoint  
**Status**: ❌ Not Implemented  
**Workaround**: Query database directly

---

## 📈 Performance Metrics

### Current System Performance

| Metric | Value |
|--------|-------|
| **Average Processing Time** | 8-12 seconds |
| **Spatial Detection Accuracy** | 94.44% |
| **Temporal Detection** | Not fully tested |
| **Forensic Detection** | ~85-91% (estimated) |
| **Overall Accuracy** | Not benchmarked |
| **Frames Analyzed** | 10 frames (spatial), 5 frames (forensic) |
| **Model Size** | ~200MB (SigLIP) |

### Resource Usage
- **CPU**: High during inference (100% for 5-8s)
- **Memory**: ~2-3GB with model loaded
- **GPU**: Utilized if available (5x faster)

---

## 🎯 Roadmap

### Phase 1: Core Functionality ✅ (Current)
- [x] Basic backend API
- [x] Spatial detection
- [x] Browser extension
- [x] Database logging

### Phase 2: Enhanced Detection ⚠️ (In Progress)
- [x] Forensic detection (basic)
- [ ] Temporal detection (advanced)
- [ ] Metadata detection
- [ ] Reasoning engine improvements

### Phase 3: Production Ready ❌ (Not Started)
- [ ] YouTube/social media support
- [ ] Result history
- [ ] Authentication
- [ ] HTTPS support

### Phase 4: Advanced Features ❌ (Future)
- [ ] ONNX browser deployment
- [ ] Heatmap generation
- [ ] Multi-platform extensions
- [ ] Cloud deployment

---

## 📝 Development Notes

### Code Quality
- ✅ Error handling with try-catch blocks
- ✅ NaN protection in scoring
- ✅ Type hints (partial)
- ⚠️ Limited docstrings
- ❌ No unit tests
- ❌ No integration tests

### Best Practices Needed
- [ ] Add comprehensive unit tests
- [ ] Add integration tests
- [ ] Improve docstrings
- [ ] Add type hints everywhere
- [ ] Code linting (pylint/flake8)
- [ ] CI/CD pipeline

---

## 🤝 Contributing

### Areas Needing Help
1. **Dataset Collection**: FaceForensics++ dataset for LSTM training
2. **Model Training**: Temporal LSTM model
3. **Frontend**: Improve extension UI/UX
4. **Testing**: Write unit and integration tests
5. **Documentation**: API documentation, tutorials

---

## 📄 License
*To be determined*

---

## 📞 Support
For issues or questions:
- Check existing conversations (see conversation history)
- Review `technical-pipeline.md` for detailed architecture
- Examine code comments in source files

---

**Last Updated**: January 26, 2026  
**Version**: 0.6.0 (60% Complete)
