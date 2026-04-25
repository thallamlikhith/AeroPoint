"""
pose_estimation.py - MediaPipe pose extractor (simple, reliable).
Returns list of frames:
{
  "frame_idx": int,
  "time": float,
  "keypoints": { "nose":[x,y], "left_shoulder":[x,y], ... }
}
"""

import cv2
import mediapipe as mp
from typing import List, Dict

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# map MediaPipe landmarks to names we use (lowercase)
LANDMARK_MAP = {
    0: "nose", 1: "left_eye", 2: "right_eye", 3: "left_ear", 4: "right_ear",
    11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow",
    15: "left_wrist", 16: "right_wrist",
    23: "left_hip", 24: "right_hip",
    25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle"
}

def _landmarks_to_kps(landmarks, w, h):
    kps = {}
    for idx, lm in enumerate(landmarks):
        name = LANDMARK_MAP.get(idx)
        if name:
            kps[name] = [int(lm.x * w), int(lm.y * h)]
    return kps

def run(video_path: str, save_annotated: bool = False, out_video_path: str = "outputs/annotated_video.mp4") -> List[Dict]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_writer = None
    if save_annotated:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(out_video_path, fourcc, fps, (w, h))

    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    frames = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        kps = {}
        if res.pose_landmarks:
            kps = _landmarks_to_kps(res.pose_landmarks.landmark, w, h)
        frames.append({"frame_idx": idx, "time": idx / (fps or 25.0), "keypoints": kps})

        # annotate
        if save_annotated:
            annotated = frame.copy()
            if res.pose_landmarks:
                mp_drawing.draw_landmarks(annotated, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            out_writer.write(annotated)

        idx += 1

    cap.release()
    if out_writer:
        out_writer.release()
    pose.close()
    return frames
