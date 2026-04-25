"""
video_utils.py - small helpers for video file metadata
"""

import cv2

def get_video_info(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {"fps": fps, "frames": count, "width": w, "height": h}

def validate_video(path):
    cap = cv2.VideoCapture(path)
    ok = cap.isOpened()
    cap.release()
    return ok
