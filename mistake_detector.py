"""
mistake_detector.py - heuristic detection returning grouped mistakes per frame.

Output (grouped):
[
  { "frame_idx": int, "time": float, "mistake_types": [...], "confidence": float, "details": "..." },
  ...
]
"""

import math
from typing import List, Dict
import numpy as np
import pandas as pd

def _angle(a, b, c):
    """Compute angle ABC at B given [x,y] points or return None."""
    try:
        a = np.array(a[:2]); b = np.array(b[:2]); c = np.array(c[:2])
        ba = a - b; bc = c - b
        denom = (np.linalg.norm(ba) * np.linalg.norm(bc))
        if denom == 0:
            return None
        cosang = np.dot(ba, bc) / denom
        cosang = float(np.clip(cosang, -1.0, 1.0))
        return float(np.degrees(np.arccos(cosang)))
    except:
        return None

def _dist(a, b):
    if a is None or b is None:
        return None
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))

def detect_mistakes(frames_kps: List[Dict], frame_rate: float = 25.0) -> List[Dict]:
    mistakes = []
    prev_wrist = None

    for f in frames_kps:
        idx = f["frame_idx"]
        t = f["time"]
        kps = f.get("keypoints", {})

        left_hip = kps.get("left_hip")
        left_knee = kps.get("left_knee")
        left_ankle = kps.get("left_ankle")

        right_hip = kps.get("right_hip")
        right_knee = kps.get("right_knee")
        right_ankle = kps.get("right_ankle")

        left_shoulder = kps.get("left_shoulder")
        right_shoulder = kps.get("right_shoulder")

        left_elbow = kps.get("left_elbow")
        right_elbow = kps.get("right_elbow")

        left_wrist = kps.get("left_wrist")
        right_wrist = kps.get("right_wrist")

        # compute angles
        lk_ang = _angle(left_hip, left_knee, left_ankle) if left_hip and left_knee and left_ankle else None
        rk_ang = _angle(right_hip, right_knee, right_ankle) if right_hip and right_knee and right_ankle else None

        le_ang = _angle(left_shoulder, left_elbow, left_wrist) if left_shoulder and left_elbow and left_wrist else None
        re_ang = _angle(right_shoulder, right_elbow, right_wrist) if right_shoulder and right_elbow and right_wrist else None

        # wrist speed
        wrist = right_wrist or left_wrist
        wrist_speed = None
        if wrist is not None and prev_wrist is not None:
            d = _dist(prev_wrist, wrist)
            wrist_speed = d * frame_rate
        prev_wrist = wrist

        types = []
        details = []

        # Rule: insufficient knee bend (angle almost straight)
        if lk_ang is not None and lk_ang > 165:
            types.append("insufficient_knee_bend_left")
            details.append(f"left_knee_angle={lk_ang:.1f}")
        if rk_ang is not None and rk_ang > 165:
            types.append("insufficient_knee_bend_right")
            details.append(f"right_knee_angle={rk_ang:.1f}")

        # Rule: weak smash prep (wrist below shoulder + elbow extended)
        if right_wrist and right_shoulder and re_ang is not None and re_ang > 150 and right_wrist[1] > right_shoulder[1]:
            types.append("weak_smash_prep_right")
            details.append(f"right_elbow={re_ang:.1f}")
        if left_wrist and left_shoulder and le_ang is not None and le_ang > 150 and left_wrist[1] > left_shoulder[1]:
            types.append("weak_smash_prep_left")
            details.append(f"left_elbow={le_ang:.1f}")

        # Rule: low wrist speed
        if wrist_speed is not None and wrist_speed < 40:
            types.append("low_wrist_speed")
            details.append(f"wrist_speed_px_s={wrist_speed:.1f}")

        if types:
            mistakes.append({
                "frame_idx": int(idx),
                "time": float(t),
                "mistake_types": types,
                "confidence": round(0.5 + 0.1 * len(types), 2),
                "details": "; ".join(details)
            })

    # group by frame (merge duplicates if multiple entries for same frame)
    if not mistakes:
        return []

    df = pd.DataFrame(mistakes)
    grouped = []
    for fi, g in df.groupby("frame_idx"):
        types = list({t for sub in g["mistake_types"] for t in sub})
        conf = float(g["confidence"].mean())
        time = float(g.iloc[0]["time"])
        details = "; ".join(g["details"].tolist())
        grouped.append({
            "frame_idx": int(fi),
            "time": time,
            "mistake_types": types,
            "confidence": conf,
            "details": details
        })

    grouped = sorted(grouped, key=lambda x: x["frame_idx"])
    return grouped
