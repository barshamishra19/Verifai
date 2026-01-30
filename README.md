# VerifAI: Multimodal AI Forensic Lab 🔍🤖

VerifAI is a powerful, multi-layered deepfake and AI-generated content detection system. It combines spatial analysis, temporal consistency checks, forensic frequency domain inspection, and metadata validation to provide a comprehensive authenticity report for videos.

## 🚀 Features

- **Spatial Analysis**: Uses deep learning (SigLIP) to detect pixel-level artifacts, skin texture inconsistencies, and facial warping.
- **Temporal Detection**: Analyzes motion smoothness and optical flow to identify the unnatural "perfection" often found in AI-generated videos.
- **Forensic Lab**: Inspections in the frequency domain (FFT) to find structured fingerprints left by GANs and Diffusion models.
- **Metadata Check**: Validates video containers, codecs, and EXIF data for signs of manipulation.
- **Browser Extension**: One-click verification directly from your browser (supports YouTube, Instagram, etc.).
- **Dynamic Calibration**: Automatically adjusts for video compression noise to reduce false positives in real social media content.

## 🏗️ Project Structure

- `backend/`: FastAPI server handling video processing and AI inference.
- `extension/`: Chrome/Edge browser extension for seamless integration.
- `models/`: Detection engines (Spatial, Temporal, Forensic, Metadata).
- `database/`: SQLite backend for tracking scan history.

## 📥 Installation

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/barshamishra19/Verifai.git
   cd Verifai/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/Scripts/activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python pipeline.py
   ```

### Browser Extension
1. Open Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension/` folder in this project.

## 🛠️ Technology Stack

- **Python & FastAPI**: High-performance backend.
- **PyTorch & Transformers**: Deep learning models for spatial detection.
- **OpenCV**: Computer vision for frame extraction and optical flow.
- **yt-dlp**: Robust video downloading from 1000+ sites.
- **Vanilla JS/CSS**: Sleek, premium browser extension UI.

## 🛡️ License
This project is for educational and forensic research purposes.

---
*Built with passion for digital truth.*
