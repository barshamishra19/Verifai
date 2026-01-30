"""
Complete metadata detector with EXIF and video codec analysis
"""
import os
from typing import Dict
from datetime import datetime

class MetadataDetector:
    """Detect metadata inconsistencies and AI generation markers"""
    
    def check_metadata(self, video_path: str) -> Dict:
        """
        Analyze video metadata for authenticity markers
        
        Args:
            video_path: Path to video file
        
        Returns:
            Dict with confidence score and details
        """
        if not os.path.exists(video_path):
            return {
                'confidence': 0.0,
                'has_anomaly': False,
                'details': 'File not found'
            }
        
        anomaly_score = 0.0
        details = []
        
        # 1. Check file creation vs modification time
        try:
            stat = os.stat(video_path)
            created = stat.st_ctime
            modified = stat.st_mtime
            
            # If modified immediately after creation, might be synthetic
            # But this is also common for downloads, so score is very low
            time_diff = abs(modified - created)
            if time_diff < 1:  # Less than 1 second difference
                anomaly_score += 0.05 # Reduced from 0.2
                details.append("File created and modified within 1 second (common in downloads)")
        except:
            pass
        
        # 2. Try to extract EXIF data
        exif_score = self._check_exif(video_path)
        anomaly_score += exif_score
        if exif_score > 0.1: # Only mention if significant
            details.append(f"EXIF anomalies detected")
        
        # 3. Try to extract codec information
        codec_score = self._check_codec(video_path)
        anomaly_score += codec_score
        if codec_score > 0.1: # Only mention if significant
            details.append(f"Codec patterns unusual")
        
        # 4. Check file size patterns
        file_size = os.path.getsize(video_path)
        # Very small files for video are suspicious
        if file_size < 50000:  # Less than 50KB (reduced from 100KB)
            anomaly_score += 0.05 # Reduced from 0.1
            details.append("Unusually small file size")
        
        # Normalize score to 0-1
        final_score = min(anomaly_score, 1.0)
        
        return {
            'confidence': final_score,
            'has_anomaly': final_score > 0.5,
            'details': ' | '.join(details) if details else 'No significant metadata anomalies',
            'file_size': file_size
        }
    
    def _check_exif(self, video_path: str) -> float:
        """
        Check EXIF data for anomalies
        
        Returns:
            Anomaly score (0-1)
        """
        try:
            import exifread
            
            with open(video_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            # AI-generated videos often lack camera-specific EXIF data
            camera_tags = ['Image Make', 'Image Model', 'EXIF DateTimeOriginal']
            found_camera_tags = sum(1 for tag in camera_tags if tag in tags)
            
            if found_camera_tags == 0:
                # No camera metadata = slightly suspicious but very common
                return 0.05 # Reduced from 0.1
            elif found_camera_tags < len(camera_tags):
                # Partial metadata = very low suspicion
                return 0.02 # Reduced from 0.05
            else:
                # Full metadata = likely real
                return 0.0
                
        except ImportError:
            # exifread not installed, skip this check
            return 0.0
        except Exception:
            # Error reading EXIF = slightly suspicious
            return 0.1 # Reduced from 0.2
    
    def _check_codec(self, video_path: str) -> float:
        """
        Check video codec and encoding parameters
        
        Returns:
            Anomaly score (0-1)
        """
        try:
            from pymediainfo import MediaInfo
            
            media_info = MediaInfo.parse(video_path)
            
            for track in media_info.tracks:
                if track.track_type == "Video":
                    # Check for common AI generation software signatures
                    encoder = str(track.encoded_library_name or '').lower()
                    
                    # 'lavf' and 'ffmpeg' are used by almost all downloaders, 
                    # so they should NOT be markers for AI.
                    ai_specific_encoders = ['sora', 'runway', 'pika']
                    if any(enc in encoder for enc in ai_specific_encoders):
                        return 0.4
                    
                    # Check frame rate (AI often uses standard rates)
                    fps = track.frame_rate
                    if fps and float(fps) in [24.0, 25.0, 30.0, 60.0]:
                        return 0.0  # Common rates are neutral
                    
            return 0.0
            
        except ImportError:
            # pymediainfo not installed, skip
            return 0.0
        except Exception:
            # Error parsing = minimal suspicion
            return 0.05 # Reduced from 0.15
