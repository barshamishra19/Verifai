"""
Enhanced forensic detector with multiple artifact detection methods
"""
import numpy as np
import cv2
from typing import Dict, List

class ForensicDetector:
    """Comprehensive forensic analysis for AI-generated video detection"""
    
    def detect_all_artifacts(self, frame: np.ndarray) -> Dict:
        """
        Run all forensic checks on a frame
        
        Args:
            frame: BGR numpy array
        
        Returns:
            Comprehensive forensic analysis results
        """
        # Run all detection methods
        fft_result = self.detect_artifacts(frame)
        gan_result = self.detect_gan_artifacts(frame)
        diffusion_result = self.detect_diffusion_artifacts(frame)
        compression_result = self.detect_compression_anomalies(frame)
        
        # Collect scores
        scores = [
            fft_result, 
            gan_result['confidence'], 
            diffusion_result['confidence'], 
            compression_result['confidence']
        ]

        # Aggregate results with weighted importance
        weights = [0.35, 0.35, 0.20, 0.10] # frequency, gan, diffusion, compression
        avg_confidence = np.average(scores, weights=weights)
        max_confidence = np.max(scores)
        
        # Calibration: If max confidence is low, and they don't agree, penalize the average
        if max_confidence < 0.6 and np.std(scores) > 0.15:
            avg_confidence *= 0.5 # More aggressive penalty
        
        # Determine dominant artifact type
        artifact_types = ['frequency', 'gan', 'diffusion', 'compression']
        dominant_type = artifact_types[np.argmax(scores)]
        
        return {
            'confidence': float(avg_confidence),
            'max_confidence': float(max_confidence),
            'dominant_artifact': dominant_type,
            'breakdown': {
                'frequency': float(fft_result),
                'gan': float(gan_result['confidence']),
                'diffusion': float(diffusion_result['confidence']),
                'compression': float(compression_result['confidence'])
            },
            'details': {
                'gan': gan_result.get('details', ''),
                'diffusion': diffusion_result.get('details', ''),
                'compression': compression_result.get('details', '')
            }
        }
    
    def detect_artifacts(self, frame: np.ndarray) -> float:
        """
        FFT-based frequency domain analysis (existing method)
        
        Args:
            frame: BGR numpy array
        
        Returns:
            Confidence score (0-1)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        rows, cols = gray.shape
        crow, ccol = rows//2, cols//2
        
        # Mask the center (low frequencies)
        mask = np.ones((rows, cols), np.uint8)
        r = 30
        mask[crow-r:crow+r, ccol-r:ccol+r] = 0
        
        f_shift_filtered = f_shift * mask
        high_freq_mean = np.mean(np.abs(f_shift_filtered))
        total_mean = np.mean(magnitude_spectrum)
        
        # Calibration: Real videos with compression often have some high-freq noise.
        # AI content typically has much more pronounced, structured artifacts.
        ratio = high_freq_mean / total_mean
        
        # New: Busy images (high std dev) naturally have more high-freq content.
        # We adjust the threshold based on the image's overall standard deviation.
        std_dev = np.std(gray)
        dynamic_threshold = 0.72 + (std_dev * 0.08) 
        
        # Adjusted threshold to be slightly more sensitive
        forensic_score = max(0.0, (ratio - dynamic_threshold) * 2.5)
        
        return float(min(forensic_score, 1.0))
    
    def detect_gan_artifacts(self, frame: np.ndarray) -> Dict:
        """
        Detect GAN-specific artifacts (block patterns, color banding)
        
        Args:
            frame: BGR numpy array
        
        Returns:
            Dict with confidence and details
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        
        # GAN block size detection using DCT
        dct = cv2.dct(gray)
        dct_abs = np.abs(dct)
        
        # Analyze block patterns
        block_strengths = []
        for block_size in [8, 16, 32]:
            for y in range(0, min(gray.shape[0] - block_size, 200), block_size):
                for x in range(0, min(gray.shape[1] - block_size, 200), block_size):
                    block = dct_abs[y:y+block_size, x:x+block_size]
                    dc_power = block[0, 0]**2
                    ac_power = np.sum(block[1:, 1:]**2)
                    strength = ac_power / (dc_power + 1e-5)
                    block_strengths.append(strength)
        
        if not block_strengths:
            return {'confidence': 0.0, 'details': 'No blocks analyzed'}
        
        # GAN: high block artifacts
        block_artifact_score = min(np.mean(block_strengths) / 100.0, 1.0)
        
        # Color banding detection
        color_frame = frame.astype(np.float32) / 255.0
        color_variances = [np.var(color_frame[:,:,i]) for i in range(3)]
        variance_uniformity = np.std(color_variances)
        
        # GAN: lower color variance (banding)
        banding_score = 1.0 - min(variance_uniformity * 10, 1.0)
        
        # Calibration: If global variance is very low (flat background), 
        # it's likely a real natural scene, not AI banding.
        global_variance = np.mean(color_variances)
        if global_variance < 0.005: 
            banding_score *= 0.5 # Discount banding in very flat scenes
            
        gan_score = 0.6 * block_artifact_score + 0.4 * banding_score
        
        details = f"Block: {block_artifact_score:.2f}, Banding: {banding_score:.2f}, Var: {global_variance:.4f}"
        
        return {
            'confidence': float(min(gan_score, 1.0)),
            'is_gan': gan_score > 0.5,
            'details': details
        }
    
    def detect_diffusion_artifacts(self, frame: np.ndarray) -> Dict:
        """
        Detect artifacts characteristic of diffusion models
        
        Args:
            frame: BGR numpy array
        
        Returns:
            Dict with confidence and details
        """
        frame_float = frame.astype(np.float32) / 255.0
        
        # Compute FFT for each channel
        fft_channels = []
        low_freq_dominance = []
        
        for i in range(3):
            fft = np.fft.fft2(frame_float[:,:,i])
            mag = np.abs(fft)
            fft_channels.append(mag)
            
            # Check low frequency dominance
            h, w = mag.shape
            center_region = mag[:h//4, :w//4]
            low_freq = np.mean(center_region)
            total_freq = np.mean(mag)
            
            if total_freq > 0:
                low_freq_dominance.append(low_freq / total_freq)
        
        # Diffusion models often have high low-frequency dominance
        avg_low_freq = np.mean(low_freq_dominance) if low_freq_dominance else 0.0
        
        # Channel misalignment (diffusion artifact)
        if len(fft_channels) == 3:
            corr_rg = np.corrcoef(fft_channels[0].flatten(), fft_channels[1].flatten())[0,1]
            corr_rb = np.corrcoef(fft_channels[0].flatten(), fft_channels[2].flatten())[0,1]
            avg_corr = (abs(corr_rg) + abs(corr_rb)) / 2
            
            # Lower correlation = more likely diffusion artifact
            misalignment_score = 1.0 - min(avg_corr, 1.0)
        else:
            misalignment_score = 0.0
        
        # Combine scores
        diffusion_score = 0.6 * avg_low_freq + 0.4 * misalignment_score
        
        details = f"Low-freq dominance: {avg_low_freq:.2f}, Channel misalignment: {misalignment_score:.2f}"
        
        return {
            'confidence': float(min(diffusion_score, 1.0)),
            'is_diffusion': diffusion_score > 0.6,
            'details': details
        }
    
    def detect_compression_anomalies(self, frame: np.ndarray) -> Dict:
        """
        Detect unusual compression patterns
        
        Args:
            frame: BGR numpy array
        
        Returns:
            Dict with confidence and details
        """
        # Convert to YCbCr for compression analysis
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # Analyze Cb and Cr channels (color components)
        cb_variance = np.var(yuv[:,:,1])
        cr_variance = np.var(yuv[:,:,2])
        color_variance = (cb_variance + cr_variance) / 2.0
        
        # Check for posterization (reduced color depth)
        # Count unique colors in each channel
        cb_unique = len(np.unique(yuv[:,:,1]))
        cr_unique = len(np.unique(yuv[:,:,2]))
        
        # Lower unique colors = more posterized
        max_possible = 256
        posterization = 1.0 - ((cb_unique + cr_unique) / (2 * max_possible))
        
        # Compression anomaly score
        variance_score = 1.0 - min(color_variance / 100.0, 1.0)
        compression_score = 0.5 * variance_score + 0.5 * posterization
        
        details = f"Color variance: {color_variance:.2f}, Posterization: {posterization:.2f}"
        
        return {
            'confidence': float(min(compression_score, 1.0)),
            'has_anomaly': compression_score > 0.6,
            'details': details
        }