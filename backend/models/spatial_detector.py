import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import numpy as np
import cv2

class SpatialDetector:
    def __init__(self):
        self.model_name = "prithivMLmods/deepfake-detector-model-v1"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = SiglipForImageClassification.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

    def detect(self, frame_array):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze()
        
        return float(probs[0].cpu()) # Fake confidence