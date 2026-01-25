import os
import time
import shutil
import uuid
import numpy as np
import math  # Added for NaN checking
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import requests
from models.spatial_detector import SpatialDetector
from models.temporal_detector import TemporalAnalyzer
from models.forensic_detector import ForensicDetector
from models.metadata_detector import MetadataDetector
from utils.video_processor import extract_frames
from utils.reasoning_engine import generate_reasoning
from database import init_db, save_analysis_result

app = FastAPI()

# --- STARTUP LOGIC ---
init_db()
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Init Engines
spatial_engine = SpatialDetector()
temporal_engine = TemporalAnalyzer()
forensic_engine = ForensicDetector()
metadata_engine = MetadataDetector()

class URLRequest(BaseModel):
    url: str

# Helper function to prevent NaN JSON errors
def safe_float(value):
    try:
        if isinstance(value, (list, np.ndarray)) and len(value) == 0:
            return 0.0
        res = float(np.mean(value)) if isinstance(value, (list, np.ndarray)) else float(value)
        return 0.0 if math.isnan(res) or math.isinf(res) else res
    except:
        return 0.0

def download_video(url: str, save_path: str):
    try:
        # NOTE: This works for direct .mp4 links. 
        # For YouTube/Shorts, you should use 'yt-dlp' library instead of requests.
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, stream=True, headers=headers, timeout=15) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Download Error: {e}")
        return False

@app.post("/api/analyze_url")
async def analyze_url(request: URLRequest):
    start_time = time.time()
    job_id = str(uuid.uuid4())
    
    filename = request.url.split("/")[-1].split("?")[0] or "video.mp4"
    if not filename.endswith(('.mp4', '.mov', '.avi')): filename += ".mp4"
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    
    if not download_video(request.url, file_path):
        raise HTTPException(status_code=400, detail="Failed to download video. Link might be private or blocked.")
    
    try:
        frames = extract_frames(file_path)
        
        # ERROR HANDLING: If no frames extracted, don't proceed to math
        if not frames or len(frames) == 0:
            raise HTTPException(status_code=422, detail="Could not process video frames. The file might be corrupted or not a valid video.")

        # 2. Run Engines with NaN protection
        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        avg_spatial = safe_float([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_motion_smoothness(frames)
        avg_temporal = safe_float(avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res)
        
        if hasattr(forensic_engine, 'detect_artifacts'):
            forensic_scores = [forensic_engine.detect_artifacts(f) for f in frames[:5]]
        else:
            forensic_scores = [0.5] 
        avg_forensic = safe_float([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = safe_float(avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res)
        
        # 3. Ensemble
        final_score = (avg_spatial * 0.30 + avg_temporal * 0.35 + avg_forensic * 0.25 + avg_metadata * 0.10)
        final_score = safe_float(final_score)
        
        classification = "AI-Generated" if final_score > 0.5 else "Real"
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(final_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        save_analysis_result(job_id, filename, report, {"spatial": avg_spatial, "temporal": avg_temporal, "forensic": avg_forensic, "metadata": avg_metadata})
        return report

    finally:
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists("temp_frames"): shutil.rmtree("temp_frames")

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    start_time = time.time()
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        frames = extract_frames(file_path)
        if not frames or len(frames) == 0:
            raise HTTPException(status_code=422, detail="No frames could be extracted from the uploaded video.")

        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        avg_spatial = safe_float([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_motion_smoothness(frames)
        avg_temporal = safe_float(avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res)
        
        if hasattr(forensic_engine, 'detect_artifacts'):
            forensic_scores = [forensic_engine.detect_artifacts(f) for f in frames[:5]]
        else:
            forensic_scores = [0.5] 
        avg_forensic = safe_float([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = safe_float(avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res)
        
        final_score = safe_float(avg_spatial * 0.30 + avg_temporal * 0.35 + avg_forensic * 0.25 + avg_metadata * 0.10)
        
        classification = "AI-Generated" if final_score > 0.5 else "Real"
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(final_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        save_analysis_result(job_id, file.filename, report, {"spatial": avg_spatial, "temporal": avg_temporal, "forensic": avg_forensic, "metadata": avg_metadata})
        return report

    finally:
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists("temp_frames"): shutil.rmtree("temp_frames")

def generate_reasoning(spatial, temporal, forensic, metadata):
    evidence = []
    if spatial > 0.7:
        evidence.append({"type": "Spatial", "explanation": "Detected distortions in skin texture/hand geometry."})
    if temporal > 0.7:
        evidence.append({"type": "Temporal", "explanation": "Movement is unnaturally smooth (Characteristic of AI)."})
    if forensic > 0.6:
        evidence.append({"type": "Forensic", "explanation": "Frequency domain spikes match GAN/Diffusion fingerprints."})
    return evidence

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)