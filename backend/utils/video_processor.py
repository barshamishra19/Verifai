import cv2
import os

def extract_frames(video_path, fps=5):
    frames = []
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    hop = int(video_fps / fps) if video_fps > fps else 1
    
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        if count % hop == 0:
            frames.append(frame)
        count += 1
    cap.release()
    return frames