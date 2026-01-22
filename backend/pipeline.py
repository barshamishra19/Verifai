import os
import time
import shutil
import uuid
import numpy as np
from fastapi import FastAPI, UploadFile, File
from models.spatial_detector import SpatialDetector
from models.temporal_detector import TemporalAnalyzer
from models.forensic_detector import ForensicDetector
from models.metadata_detector import MetadataDetector
from utils.video_processor import extract_frames
from utils.reasoning_engine import generate_reasoning
from database import init_db, save_analysis_result # 👈 Added DB Import

app = FastAPI()

# --- STARTUP LOGIC ---
init_db() # 👈 Initialize Database Table
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Init Engines (Keeping your original names)
spatial_engine = SpatialDetector()
temporal_engine = TemporalAnalyzer()
forensic_engine = ForensicDetector()
metadata_engine = MetadataDetector()

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import requests

# ... (Previous imports)

class URLRequest(BaseModel):
    url: str

def download_video(url: str, save_path: str):
    try:
        with requests.get(url, stream=True) as r:
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
    
    # Use generic name or try to extract from URL
    filename = request.url.split("/")[-1] or "video.mp4"
    if "?" in filename: filename = filename.split("?")[0]
    if not filename.endswith(('.mp4', '.mov', '.avi')): filename += ".mp4"
    
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    
    # Download
    if not download_video(request.url, file_path):
        raise HTTPException(status_code=400, detail="Failed to download video from URL")
    
    # Reuse Analysis Logic
    try:
        # 1. Process Frames
        frames = extract_frames(file_path)
        
        # 2. Run All Engines
        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        avg_spatial = np.mean([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_motion_smoothness(frames)
        avg_temporal = avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res
        
        if hasattr(forensic_engine, 'detect_artifacts'):
            forensic_scores = [forensic_engine.detect_artifacts(f) for f in frames[:5]]
        else:
            forensic_scores = [0.5] 
        avg_forensic = np.mean([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res
        
        # 3. Ensemble
        final_score = (
            avg_spatial * 0.30 +
            avg_temporal * 0.35 +
            avg_forensic * 0.25 +
            avg_metadata * 0.10
        )
        
        classification = "AI-Generated" if final_score > 0.5 else "Real"
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(final_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": (time.time() - start_time) * 1000
        }

        # 4. SAVE TO DATABASE
        breakdown = {
            "spatial": avg_spatial, "temporal": avg_temporal,
            "forensic": avg_forensic, "metadata": avg_metadata
        }
        save_analysis_result(job_id, filename, report, breakdown)
        
        return report

    finally:
        # 5. CLEANUP
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("temp_frames"):
            shutil.rmtree("temp_frames")

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    start_time = time.time()
    job_id = str(uuid.uuid4()) # 👈 Unique Job ID
    
    # SAVE VIDEO TO UPLOADS FOLDER (Not root)
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # 1. Process Frames
        frames = extract_frames(file_path) # 👈 Using the new path
        
        # 2. Run All Engines (Keeping your original logic)
        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        # Extracting confidence if the engines return a dict
        avg_spatial = np.mean([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_motion_smoothness(frames)
        avg_temporal = avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res
        
        # Checking if forensic_engine is a class instance or static method
        if hasattr(forensic_engine, 'detect_artifacts'):
            forensic_scores = [forensic_engine.detect_artifacts(f) for f in frames[:5]]
        else:
            # Fallback for different implementations
            forensic_scores = [0.5] 
        avg_forensic = np.mean([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res
        
        # 3. Ensemble (Blueprint Weights: 30%, 35%, 25%, 10%)
        final_score = (
            avg_spatial * 0.30 +
            avg_temporal * 0.35 +
            avg_forensic * 0.25 +
            avg_metadata * 0.10
        )
        
        classification = "AI-Generated" if final_score > 0.5 else "Real"
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(final_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": (time.time() - start_time) * 1000
        }

        # 4. SAVE TO DATABASE 👈 Added DB Save
        breakdown = {
            "spatial": avg_spatial, "temporal": avg_temporal,
            "forensic": avg_forensic, "metadata": avg_metadata
        }
        save_analysis_result(job_id, file.filename, report, breakdown)
        
        return report

    finally:
        # 5. CLEANUP LOGIC 👈 Added File/Folder Deletion
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted uploaded video: {file_path}")
        
        if os.path.exists("temp_frames"):
            shutil.rmtree("temp_frames")
            print("🧹 Cleaned up temp_frames")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)