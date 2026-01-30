"""
Enhanced temporal analyzer with multiple detection methods
"""
import cv2
import numpy as np
from typing import Dict, List

class TemporalAnalyzer:
    """Temporal consistency analysis for AI-generated video detection"""
    
    def detect_all_temporal(self, frames: List[np.ndarray]) -> Dict:
        """
        Run all temporal detection methods
        
        Args:
            frames: List of BGR frame arrays
        
        Returns:
            Comprehensive temporal analysis results
        """
        if not frames or len(frames) < 2:
            return {
                'confidence': 0.0,
                'has_anomaly': False,
                'details': 'Insufficient frames for temporal analysis'
            }
        
        # Run all detection methods
        motion_result = self.detect_motion_smoothness(frames)
        lipsync_result = self.detect_lip_sync_errors(frames)
        blink_result = self.detect_blink_anomalies(frames)
        
        # Aggregate scores
        scores = [
            motion_result.get('confidence', 0.0),
            lipsync_result.get('confidence', 0.0),
            blink_result.get('confidence', 0.0)
        ]
        
        valid_scores = [s for s in scores if s > 0]
        avg_confidence = np.mean(valid_scores) if valid_scores else 0.0
        
        anomalies = []
        if motion_result.get('has_smooth_motion_anomaly', False):
            anomalies.append('smooth_motion')
        if lipsync_result.get('has_lip_sync_error', False):
            anomalies.append('lip_sync')
        if blink_result.get('has_blink_anomaly', False):
            anomalies.append('blink_pattern')
        
        return {
            'confidence': float(avg_confidence),
            'has_anomaly': len(anomalies) > 0,
            'anomaly_types': anomalies,
            'breakdown': {
                'motion_smoothness': float(motion_result.get('confidence', 0.0)),
                'lip_sync': float(lipsync_result.get('confidence', 0.0)),
                'blink_pattern': float(blink_result.get('confidence', 0.0))
            },
            'details': {
                'motion': motion_result.get('description', ''),
                'lipsync': lipsync_result.get('description', ''),
                'blink': blink_result.get('description', '')
            }
        }
    
    def detect_motion_smoothness(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect unnaturally smooth motion (characteristic of AI)
        
        Args:
            frames: List of BGR frames
        
        Returns:
            Motion smoothness analysis results
        """
        if len(frames) < 2:
            return {
                'has_smooth_motion_anomaly': False,
                'confidence': 0.0,
                'description': 'Insufficient frames'
            }
        
        # Compute optical flow between frames
        flow_magnitudes = []
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        
        for frame in frames[1:]:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).mean()
            flow_magnitudes.append(magnitude)
            prev_gray = gray
        
        if not flow_magnitudes:
            return {
                'has_smooth_motion_anomaly': False,
                'confidence': 0.0,
                'description': 'No flow computed'
            }
        
        # Real video has jittery motion (high variance)
        # AI video is too smooth (low variance)
        # Increased smoothing factor for variance to reduce sensitivity to minor stability
        motion_variance = np.var(flow_magnitudes)
        
        # Calibration: If motion is extremely low (static camera/webcam), 
        # reduce the AI confidence score as real static videos look "smooth".
        activity_level = np.mean(flow_magnitudes)
        # Increased activity floor to 0.8 to be safer
        if activity_level < 0.8: 
            # For static scenes, we can't reliably use motion smoothness as an AI indicator
            motion_consistency = 0.05 * (activity_level / 0.8) 
        else:
            # Real videos have natural jitter. Even "smooth" real videos have more 
            # variance than AI. Increased denominator to 25 to lower baseline confidence.
            motion_consistency = 1.0 - (motion_variance / (motion_variance + 25))
            
        # Ensure consistency is within bounds
        motion_consistency = max(0.0, min(1.0, motion_consistency))
        
        return {
            'has_smooth_motion_anomaly': motion_consistency > 0.75,
            'confidence': float(motion_consistency),
            'anomaly_frames': [],
            'description': f'Motion smoothness: {motion_consistency:.2f} (Activity: {activity_level:.3f})'
        }
    
    def detect_lip_sync_errors(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect lip-sync errors between video frames
        
        Args:
            frames: List of BGR frames
        
        Returns:
            Lip-sync analysis results
        """
        # Extract mouth region from frames
        mouth_regions = []
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        for frame in frames[:min(len(frames), 30)]:  # Analyze first 30 frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) > 0:
                x, y, w, h = faces[0]
                # Extract mouth region (lower half of face)
                mouth = frame[y+h//2:y+h, x:x+w]
                if mouth.size > 0:
                    mouth_regions.append(cv2.resize(mouth, (64, 64)))
        
        if len(mouth_regions) < 5:
            return {
                'has_lip_sync_error': False,
                'confidence': 0.0,
                'anomaly_frames': [],
                'description': 'Insufficient face detections for lip-sync analysis'
            }
        
        # Analyze mouth movement consistency
        mouth_changes = []
        for i in range(len(mouth_regions) - 1):
            diff = cv2.absdiff(mouth_regions[i], mouth_regions[i+1])
            change_amount = np.mean(diff)
            mouth_changes.append(change_amount)
        
        if not mouth_changes:
            return {
                'has_lip_sync_error': False,
                'confidence': 0.0,
                'anomaly_frames': [],
                'description': 'No mouth movements detected'
            }
        
        # Detect anomalies (sudden jumps or flatness)
        mean_change = np.mean(mouth_changes)
        std_change = np.std(mouth_changes)
        
        anomaly_frames = []
        for i, change in enumerate(mouth_changes):
            if abs(change - mean_change) > 2 * std_change:
                anomaly_frames.append(i)
        
        confidence = min(len(anomaly_frames) / max(len(mouth_changes), 1), 1.0)
        
        return {
            'has_lip_sync_error': confidence > 0.3,
            'confidence': float(confidence),
            'anomaly_frames': anomaly_frames,
            'description': f'Lip-sync inconsistency in {len(anomaly_frames)}/{len(mouth_changes)} transitions'
        }
    
    def detect_blink_anomalies(self, frames: List[np.ndarray]) -> Dict:
        """
        Detect unnatural blink patterns (AI often has irregular blinking)
        
        Args:
            frames: List of BGR frames
        
        Returns:
            Blink pattern analysis results
        """
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        blink_sequence = []
        for frame in frames[:min(len(frames), 60)]:  # Analyze first 60 frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
            blink_sequence.append(len(eyes) >= 2)  # True if both eyes detected
        
        if len(blink_sequence) < 10:
            return {
                'has_blink_anomaly': False,
                'confidence': 0.0,
                'anomaly_frames': [],
                'description': 'Insufficient frames for blink analysis'
            }
        
        # Count blink transitions (eyes disappearing/reappearing)
        blink_changes = sum(1 for i in range(len(blink_sequence)-1) 
                           if blink_sequence[i] != blink_sequence[i+1])
        
        # Normal: 1-3 blinks per 30 frames (at 30fps = 1 second)
        # Calculate expected blinks
        expected_blinks = len(blink_sequence) / 30 * 2  # ~2 blinks per second
        
        # Ratio of actual vs expected
        if expected_blinks > 0:
            blink_ratio = blink_changes / expected_blinks
        else:
            blink_ratio = 0.0
        
        # Abnormal if too few or too many blinks
        if blink_ratio < 0.2: # Reduced from 0.3
            # Too few blinks (characteristic of AI)
            confidence = (1.0 - (blink_ratio / 0.2)) * 0.8 # Capped at 0.8
            has_anomaly = True
        elif blink_ratio > 4.0: # Increased from 3.0
            # Too many blinks (also suspicious)
            confidence = min((blink_ratio - 4.0) / 5.0, 0.7) # Capped at 0.7
            has_anomaly = True
        else:
            confidence = 0.0
            has_anomaly = False
        
        return {
            'has_blink_anomaly': has_anomaly,
            'confidence': float(confidence),
            'anomaly_frames': [],
            'description': f'Blink frequency: {blink_changes} (expected ~{expected_blinks:.1f})'
        }