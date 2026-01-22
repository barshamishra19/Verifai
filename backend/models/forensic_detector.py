import numpy as np
import cv2

class ForensicDetector:
    def detect_artifacts(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # Identify frequency spikes (Artificial patterns often manifest as high freq)
        rows, cols = gray.shape
        crow, ccol = rows//2, cols//2
        
        # Mask the center (low frequencies)
        mask = np.ones((rows, cols), np.uint8)
        r = 30
        mask[crow-r:crow+r, ccol-r:ccol+r] = 0
        
        f_shift_filtered = f_shift * mask
        high_freq_mean = np.mean(np.abs(f_shift_filtered))
        total_mean = np.mean(magnitude_spectrum)
        
        # Ratio of high frequency energy to total
        # Natural images have very little high freq energy relative to total (Power Law)
        # AI artifacts may increase this
        if total_mean == 0: return 0.0
        
        # Scaling factor 5 derived empirically (Reduced from 20 to avoid saturation)
        # Scaling factor derived from empirical observation:
        # Real ~ 0.62 -> (0.12 * 3) = 0.36
        # AI ~ 0.82 -> (0.32 * 3) = 0.96
        ratio = high_freq_mean / total_mean
        forensic_score = max(0.0, (ratio - 0.5) * 3)
        return float(min(forensic_score, 1.0))