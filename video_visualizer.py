"""
video_visualizer.py - small helpers to draw on frames if needed
"""

import cv2

def draw_point(frame, point, color=(0,255,0), radius=4):
    if point and len(point) >= 2:
        cv2.circle(frame, (int(point[0]), int(point[1])), radius, color, -1)
    return frame

def draw_label(frame, text, x=10, y=30, color=(255,255,255)):
    cv2.putText(frame, str(text), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    return frame
