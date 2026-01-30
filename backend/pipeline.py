import os
import time
import shutil
import uuid
import numpy as np
import math
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Internal Imports
from models.spatial_detector import SpatialDetector
from models.temporal_detector import TemporalAnalyzer
from models.forensic_detector import ForensicDetector
from models.metadata_detector import MetadataDetector
from utils.video_processor import extract_frames
from utils.reasoning_engine import generate_reasoning
from utils.video_downloader import download_video
from database import init_db, save_analysis_result

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Success", "message": "VerifAI Backend is Running"}

# Initialize
init_db()
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

spatial_engine = SpatialDetector()
temporal_engine = TemporalAnalyzer()
forensic_engine = ForensicDetector()
metadata_engine = MetadataDetector()

class URLRequest(BaseModel):
    url: str

def safe_float(value):
    try:
        if isinstance(value, (list, np.ndarray)) and len(value) == 0:
            return 0.0
        res = float(np.mean(value)) if isinstance(value, (list, np.ndarray)) else float(value)
        return 0.0 if math.isnan(res) or math.isinf(res) else res
    except:
        return 0.0

@app.post("/api/analyze_url")
async def analyze_url(request: URLRequest):
    start_time = time.time()
    job_id = str(uuid.uuid4())
    
    # 1. Validate URL
    video_url = request.url.strip()
    if not video_url:
        raise HTTPException(status_code=400, detail="URL is empty")

    print(f"🔍 Analyzing URL: {video_url}")
    
    # Create filename
    filename = f"{job_id}_video.mp4"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 2. Download
    print(f"📥 Downloading video...")
    success, error_msg = download_video(video_url, file_path)
    
    if not success:
        print(f"❌ Download failed: {error_msg}")
        raise HTTPException(status_code=400, detail=f"Download failed: {error_msg}")
    
    try:
        # 3. Process Video
        frames = extract_frames(file_path)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video.")

        # 4. Run Engines
        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        avg_spatial = safe_float([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_all_temporal(frames)
        avg_temporal = safe_float(avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res)
        
        forensic_scores = [forensic_engine.detect_all_artifacts(f) for f in frames[:5]]
        avg_forensic = safe_float([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = safe_float(avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res)
        
        # 5. Ensemble Calculation (Refined for Higher Sensitivity)
        # We use a weighted average, but also check for "Red Flags"
        base_score = (avg_spatial * 0.35 + avg_temporal * 0.30 + avg_forensic * 0.25 + avg_metadata * 0.10)
        
        # Red Flag: If Spatial or Forensic is extremely confident, AI detection is likely
        # even if other engines (like Temporal) are confused by video quality.
        red_flag_boost = 0
        if avg_spatial > 0.8: red_flag_boost = max(red_flag_boost, 0.2)
        if avg_forensic > 0.75: red_flag_boost = max(red_flag_boost, 0.2)
        
        final_score = safe_float(base_score + red_flag_boost)
        
        # Classification threshold back to 0.50 for better sensitivity
        classification = "AI-Generated" if final_score > 0.50 else "Real"
        
        display_score = final_score
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(display_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        save_analysis_result(job_id, filename, report, {
            "spatial": avg_spatial, "temporal": avg_temporal, 
            "forensic": avg_forensic, "metadata": avg_metadata
        })
        return report

    finally:
        # Cleanup
        if os.path.exists(file_path): 
            try: os.remove(file_path)
            except: pass
        if os.path.exists("temp_frames"): 
            try: shutil.rmtree("temp_frames")
            except: pass

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    start_time = time.time()
    job_id = str(uuid.uuid4())
    
    # Create filename and save
    filename = f"{job_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Process Video (Same logic as analyze_url)
        frames = extract_frames(file_path)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video.")

        # Run Engines
        spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
        avg_spatial = safe_float([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
        
        avg_temporal_res = temporal_engine.detect_all_temporal(frames)
        avg_temporal = safe_float(avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res)
        
        forensic_scores = [forensic_engine.detect_all_artifacts(f) for f in frames[:5]]
        avg_forensic = safe_float([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
        
        avg_metadata_res = metadata_engine.check_metadata(file_path)
        avg_metadata = safe_float(avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res)
        
        # Ensemble Calculation (Refined for Higher Sensitivity)
        base_score = (avg_spatial * 0.35 + avg_temporal * 0.30 + avg_forensic * 0.25 + avg_metadata * 0.10)
        
        # Red Flag: If Spatial or Forensic is extremely confident, AI detection is likely
        red_flag_boost = 0
        if avg_spatial > 0.8: red_flag_boost = max(red_flag_boost, 0.2)
        if avg_forensic > 0.75: red_flag_boost = max(red_flag_boost, 0.2)
        
        final_score = safe_float(base_score + red_flag_boost)
        classification = "AI-Generated" if final_score > 0.50 else "Real"
        
        display_score = final_score
        evidence = generate_reasoning(avg_spatial, avg_temporal, avg_forensic, avg_metadata)
        
        report = {
            "job_id": job_id,
            "final_confidence": round(display_score, 4),
            "classification": classification,
            "evidence": evidence,
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        save_analysis_result(job_id, filename, report, {
            "spatial": avg_spatial, "temporal": avg_temporal, 
            "forensic": avg_forensic, "metadata": avg_metadata
        })
        return report

    finally:
        # Cleanup
        if os.path.exists(file_path): 
            try: os.remove(file_path)
            except: pass

@app.get("/api/history")
async def get_history():
    from database import get_analysis_history
    return get_analysis_history(limit=50)

@app.get("/api/stats")
async def get_stats():
    from database import get_statistics
    return get_statistics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)