"""
pipeline.py - simplified pipeline for mistake detection only.

run_pipeline(video_path) -> returns dict with:
 - mistakes_grouped: grouped per frame (list)
 - mistakes_expanded: list with one dict per mistake type (includes image path)
 - annotated_video: path (if created)
 - outputs in outputs/ folder
"""

import os
import json
from pathlib import Path

from pose_estimation import run as run_pose
from mistake_detector import detect_mistakes

# outputs
BASE = Path("outputs")
BASE.mkdir(exist_ok=True)
FRAMES = BASE / "frames"
FRAMES.mkdir(exist_ok=True)

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def _extract_frame(video_path: str, frame_idx: int, out_path: str):
    import cv2
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_idx))
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(out_path, frame)
    cap.release()

def run_pipeline(video_path: str):
    """
    Run pose estimation + mistake detection.
    Returns a dict of results.
    """
    # No .env / API required for this simplified version
    video_path = str(video_path)

    # 1) Pose estimation (returns list of frames with keypoints)
    frames = run_pose(video_path, save_annotated=False)

    # 2) Detect mistakes (grouped per frame)
    grouped = detect_mistakes(frames)

    # Save grouped JSON
    grouped_path = BASE / "analysis_summary.json"
    save_json(grouped, grouped_path)

    # 3) Expand grouped into one entry per mistake type (user wanted option B)
    expanded = []
    for g in grouped:
        frame_idx = g["frame_idx"]
        time = g["time"]
        conf = g.get("confidence", None)
        details = g.get("details", "")
        for mt in g.get("mistake_types", []):
            # extract frame image for this mistake type (image per entry)
            img_name = f"frame_{int(frame_idx):06d}_{mt}.jpg"
            img_path = str(FRAMES / img_name)
            _extract_frame(video_path, frame_idx, img_path)
            expanded.append({
                "frame_idx": int(frame_idx),
                "time": float(time),
                "mistake_type": mt,
                "confidence": conf,
                "details": details,
                "image": img_path
            })

    # Save expanded CSV and JSON
    expanded_path = BASE / "mistakes_expanded.json"
    save_json(expanded, expanded_path)
    # also write CSV
    try:
        import pandas as pd
        if expanded:
            df = pd.DataFrame(expanded)
            df.to_csv(BASE / "mistakes_expanded.csv", index=False)
    except Exception:
        pass

    return {
        "mistakes_grouped": str(grouped_path),
        "mistakes_expanded": expanded,
        "annotated_video": None,
        "outputs_dir": str(BASE)
    }
