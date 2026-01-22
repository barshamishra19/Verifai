import cv2
import numpy as np
import sys
import os

# Add current directory to path so we can import models
sys.path.append(os.getcwd())

from models.spatial_detector import SpatialDetector
from models.temporal_detector import TemporalAnalyzer
from models.forensic_detector import ForensicDetector
from models.metadata_detector import MetadataDetector
from utils.video_processor import extract_frames

def debug_video(video_path):
    with open("results.txt", "w") as out:
        out.write(f"Analyzing {video_path}...\n")
        
        try:
            frames = extract_frames(video_path)
            out.write(f"Extracted {len(frames)} frames.\n")
        except Exception as e:
            out.write(f"Error extracting frames: {e}\n")
            return

        # Initialize engines
        out.write("Initializing engines...\n")
        try:
            spatial_engine = SpatialDetector()
            temporal_engine = TemporalAnalyzer()
            forensic_engine = ForensicDetector()
            metadata_engine = MetadataDetector()
        except Exception as e:
            out.write(f"Error initializing engines: {e}\n")
            return

        # 1. Spatial
        out.write("Running Spatial Detector...\n")
        try:
            spatial_scores = [spatial_engine.detect(f) for f in frames[:10]]
            avg_spatial = np.mean([res['fake_confidence'] if isinstance(res, dict) else res for res in spatial_scores])
            out.write(f"Spatial Scores: {spatial_scores}\n")
            out.write(f"Avg Spatial: {avg_spatial}\n")
        except Exception as e:
            out.write(f"Spatial error: {e}\n")
            avg_spatial = 0

        # 2. Temporal
        out.write("Running Temporal Detector...\n")
        try:
            avg_temporal_res = temporal_engine.detect_motion_smoothness(frames)
            avg_temporal = avg_temporal_res['confidence'] if isinstance(avg_temporal_res, dict) else avg_temporal_res
            out.write(f"Temporal Score: {avg_temporal}\n")
        except Exception as e:
            out.write(f"Temporal error: {e}\n")
            avg_temporal = 0

        # 3. Forensic
        out.write("Running Forensic Detector...\n")
        try:
            if hasattr(forensic_engine, 'detect_artifacts'):
                forensic_scores = [forensic_engine.detect_artifacts(f) for f in frames[:5]]
            else:
                forensic_scores = [0.5]
            avg_forensic = np.mean([res['confidence'] if isinstance(res, dict) else res for res in forensic_scores])
            out.write(f"Forensic Scores: {forensic_scores}\n")
            out.write(f"Avg Forensic: {avg_forensic}\n")
        except Exception as e:
            out.write(f"Forensic error: {e}\n")
            avg_forensic = 0

        # 4. Metadata
        avg_metadata_res = metadata_engine.check_metadata(video_path)
        avg_metadata = avg_metadata_res['confidence'] if isinstance(avg_metadata_res, dict) else avg_metadata_res
        out.write(f"Metadata Score: {avg_metadata}\n")

        # Final calculation
        final_score = (
            avg_spatial * 0.30 +
            avg_temporal * 0.35 +
            avg_forensic * 0.25 +
            avg_metadata * 0.10
        )
        
        out.write(f"\nFINAL SCORE: {final_score}\n")
        out.write(f"Classification: {'AI-Generated' if final_score > 0.5 else 'Real'}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Default to the one found in the file list
        video_path = "temp_WIN_20260118_21_04_04_Pro.mp4"
    
    if os.path.exists(video_path):
        debug_video(video_path)
    else:
        print(f"File not found: {video_path}")
