import cv2
import numpy as np

class TemporalAnalyzer:
    def detect_motion_smoothness(self, frames):
        if len(frames) < 2: return 0.0
        
        flow_magnitudes = []
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        
        for frame in frames[1:]:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean()
            flow_magnitudes.append(magnitude)
            prev_gray = gray
        
        # Real videos have natural consistency; AI often has temporal flickering (jitter)
        motion_variance = np.var(flow_magnitudes)
        # Low variance (smooth) -> Low score (Real)
        # High variance (jittery) -> High score (AI-Generated)
        # Using a sigmoid-like mapping or simple ratio
        temporal_score = motion_variance / (motion_variance + 1.0) # Adjusted constant for sensitivity
        
        return float(temporal_score)