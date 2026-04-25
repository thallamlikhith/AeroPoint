"""
streamlit_app.py - Advanced Badminton Mistake Detector
Professional UI with analytics, visualizations, and export options
"""

import streamlit as st
from pathlib import Path
import tempfile
import io
import csv
import zipfile
import json
from datetime import datetime
import base64
import os
import matplotlib
matplotlib.use('Agg')  # Prevents loading the blocked font engine
os.environ['PYTHON_PIL_IMAGE_MAX_SIZE'] = '0' # Prevents some image-based blocks

# Local imports
from pipeline import run_pipeline

# Version compatibility
STREAMLIT_VERSION = st.__version__
USE_CONTAINER_WIDTH = tuple(map(int, STREAMLIT_VERSION.split('.')[:2])) >= (1, 2)

# Page config
st.set_page_config(
    page_title="Badminton AI Coach",
    layout="wide",
    page_icon="🏸",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #FF6B6B;
        --secondary: #4ECDC4;
        --accent: #FFE66D;
        --dark: #2C3E50;
        --light: #ECF0F1;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #555;
        margin-top: 0.5rem;
    }
    
    /* Mistake card */
    .mistake-card {
        background: white;
        border-left: 5px solid #FF6B6B;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .mistake-card.warning {
        border-left-color: #FFE66D;
    }
    
    .mistake-card.info {
        border-left-color: #4ECDC4;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00acc1;
        margin: 1rem 0;
    }
    
    /* Timeline */
    .timeline-item {
        position: relative;
        padding-left: 30px;
        margin-bottom: 20px;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 5px;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        background: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏸 AI Badminton Coach</h1>
    <p>Advanced mistake detection powered by computer vision and AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; font-size: 4rem; padding: 1rem;'>
        🏸
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📊 Analysis Settings")
    
    # Settings
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Minimum confidence level for mistake detection"
    )
    
    show_timeline = st.checkbox("Show Timeline View", value=True)
    show_analytics = st.checkbox("Show Analytics Dashboard", value=True)
    auto_download = st.checkbox("Auto-download results", value=False)
    
    st.markdown("---")
    st.markdown("### 📚 Mistake Categories")
    st.markdown("""
    - **Footwork**: Positioning & movement
    - **Grip**: Racket handling
    - **Stance**: Body positioning
    - **Swing**: Stroke mechanics
    - **Follow-through**: Post-shot motion
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This AI-powered system analyzes badminton videos to detect technique mistakes 
    and provide actionable feedback for improvement.
    """)

# Main content
uploaded = st.file_uploader(
    "📤 Upload Your Badminton Video",
    type=["mp4", "mov", "avi", "mkv"],
    help="Supported formats: MP4, MOV, AVI, MKV"
)

if uploaded is None:
    # Show getting started section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <div style='font-size: 4rem;'>📹</div>
            <h3>1. Upload Video</h3>
            <p>Upload your badminton match or training video</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <div style='font-size: 4rem;'>🤖</div>
            <h3>2. AI Analysis</h3>
            <p>Our AI analyzes your technique and posture</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <div style='font-size: 4rem;'>📊</div>
            <h3>3. Get Feedback</h3>
            <p>Receive detailed insights and improvement tips</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 Tips for best results:</strong>
        <ul>
            <li>Record from a side angle for better pose detection</li>
            <li>Ensure good lighting and minimal background clutter</li>
            <li>Keep the player fully visible in frame</li>
            <li>Video length: 10 seconds to 5 minutes recommended</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Save uploaded file
tmpdir = tempfile.mkdtemp()
video_path = Path(tmpdir) / uploaded.name
with open(video_path, "wb") as f:
    f.write(uploaded.read())

# Video preview
st.markdown("### 📺 Video Preview")
video_col, info_col = st.columns([2, 1])

with video_col:
    st.video(str(video_path))

with info_col:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                padding: 1.5rem; border-radius: 12px;'>
        <h4>📋 Video Info</h4>
    """, unsafe_allow_html=True)
    st.write(f"**Filename:** {uploaded.name}")
    st.write(f"**Size:** {uploaded.size / 1024 / 1024:.2f} MB")
    st.write(f"**Uploaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("</div>", unsafe_allow_html=True)

# Analysis button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🚀 Start AI Analysis")

if analyze_button:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Stage 1: Pose Estimation
    status_text.markdown("**Stage 1/3:** 🎯 Running pose estimation...")
    progress_bar.progress(33)
    
    try:
        with st.spinner("Processing video..."):
            results = run_pipeline(str(video_path))
        
        # Stage 2: Mistake Detection
        status_text.markdown("**Stage 2/3:** 🔍 Detecting mistakes...")
        progress_bar.progress(66)
        
        # Stage 3: Analysis Complete
        status_text.markdown("**Stage 3/3:** ✅ Generating report...")
        progress_bar.progress(100)
        
        mistakes = results.get("mistakes_expanded", [])
        
        # Filter by confidence
        mistakes = [m for m in mistakes if m.get("confidence", 1.0) >= confidence_threshold]
        
        status_text.empty()
        progress_bar.empty()
        
        if not mistakes:
            st.success("🎉 Great job! No significant mistakes detected.")
            st.balloons()
            st.stop()
        
        st.success(f"✅ Analysis complete! Found {len(mistakes)} areas for improvement.")
        
        # Store results in session state
        st.session_state.results = results
        st.session_state.mistakes = mistakes
        
    except Exception as e:
        st.error(f"❌ Pipeline error: {e}")
        st.stop()

# Display results if available
if 'mistakes' in st.session_state:
    mistakes = st.session_state.mistakes
    
    # Analytics Dashboard
    if show_analytics:
        st.markdown("---")
        st.markdown("## 📊 Performance Analytics")
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        mistake_types = [m["mistake_type"] for m in mistakes]
        unique_types = set(mistake_types)
        avg_confidence = sum(m.get("confidence", 0) for m in mistakes) / len(mistakes) if mistakes else 0
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-value">{len(mistakes)}</p>
                <p class="stat-label">Total Issues</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-value">{len(unique_types)}</p>
                <p class="stat-label">Mistake Types</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-value">{avg_confidence:.1%}</p>
                <p class="stat-label">Avg Confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            priority_issues = sum(1 for m in mistakes if m.get("confidence", 0) > 0.8)
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-value">{priority_issues}</p>
                <p class="stat-label">Priority Issues</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.markdown("### 📈 Mistake Distribution")
        chart_col1, chart_col2 = st.columns(2)
        
        import pandas as pd
        
        with chart_col1:
            # Mistake type distribution
            type_counts = pd.Series(mistake_types).value_counts()
            st.json(dict(type_counts))
        
        with chart_col2:
            # Timeline scatter
            timeline_df = pd.DataFrame([{
                "Time (s)": m["time"],
                "Confidence": m.get("confidence", 0.5)
            } for m in mistakes])
            safe_data = timeline_df.to_dict('records')
            st.line_chart(safe_data, x="Time (s)", y="Confidence")
    
    # Timeline View
    if show_timeline:
        st.markdown("---")
        st.markdown("## ⏱️ Timeline View")
        
        sorted_mistakes = sorted(mistakes, key=lambda x: x["time"])
        
        for i, m in enumerate(sorted_mistakes):
            timestamp = f"{int(m['time'] // 60):02d}:{int(m['time'] % 60):02d}"
            confidence_pct = m.get("confidence", 0) * 100
            
            card_class = "mistake-card"
            if confidence_pct > 80:
                card_class += " warning"
            elif confidence_pct < 50:
                card_class += " info"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.2rem;">{m['mistake_type']}</strong>
                        <span style="margin-left: 1rem; color: #666;">⏱️ {timestamp}</span>
                    </div>
                    <div style="background: {'#FF6B6B' if confidence_pct > 80 else '#4ECDC4'}; 
                                color: white; padding: 0.5rem 1rem; border-radius: 20px;">
                        {confidence_pct:.0f}%
                    </div>
                </div>
                {f'<p style="margin-top: 0.5rem; color: #555;">{m.get("details", "")}</p>' if m.get("details") else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed Results
    st.markdown("---")
    st.markdown("## 🔍 Detailed Analysis")
    
    # Table view
    df = pd.DataFrame([{
        "⏱️ Time": f"{int(m['time'] // 60):02d}:{int(m['time'] % 60):02d}",
        "🎯 Mistake Type": m["mistake_type"],
        "📊 Confidence": f"{m.get('confidence', 0):.1%}",
        "📝 Details": m.get("details", "")[:50] + "..." if len(m.get("details", "")) > 50 else m.get("details", ""),
        "🖼️ Image": "✓" if m.get("image") else "✗"
    } for m in mistakes])
    
    st.dataframe(df, hide_index=True)
    
    # Image Gallery
    st.markdown("### 🖼️ Mistake Image Gallery")
    
    # Filter controls
    filter_col1, filter_col2 = st.columns([3, 1])
    with filter_col1:
        selected_types = st.multiselect(
            "Filter by mistake type",
            options=sorted(unique_types),
            default=sorted(unique_types)
        )
    with filter_col2:
        images_per_row = st.select_slider("Images per row", options=[1, 2, 3, 4], value=3)
    
    filtered_mistakes = [m for m in mistakes if m["mistake_type"] in selected_types]
    
    # Display images in grid
    cols = st.columns(images_per_row)
    for i, m in enumerate(filtered_mistakes):
        col = cols[i % images_per_row]
        
        with col:
            st.markdown(f"""
            <div style='background: white; padding: 1rem; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                <strong>{m['mistake_type']}</strong><br>
                <small>⏱️ {m['time']:.2f}s | 📊 {m.get('confidence', 0):.0%}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if m.get("image") and Path(m["image"]).exists():
                if USE_CONTAINER_WIDTH:
                    st.image(str(m["image"]), use_column_width=True)
                else:
                    st.image(str(m["image"]))
            else:
                st.info("Image not available")
    
    # Export Section
    st.markdown("---")
    st.markdown("## 💾 Export Results")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # CSV Download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        
        st.download_button(
            "📄 Download CSV Report",
            data=csv_bytes,
            file_name=f"badminton_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with export_col2:
        # JSON Download
        json_data = json.dumps(mistakes, indent=2)
        st.download_button(
            "📋 Download JSON Data",
            data=json_data,
            file_name=f"badminton_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with export_col3:
        # ZIP Download
        images = [m["image"] for m in mistakes if m.get("image") and Path(m["image"]).exists()]
        if images:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for img_path in images:
                    p = Path(img_path)
                    zf.write(p, arcname=p.name)
            zip_buffer.seek(0)
            
            st.download_button(
                "🖼️ Download Images (ZIP)",
                data=zip_buffer,
                file_name=f"mistake_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
    
    # Recommendations
    st.markdown("---")
    st.markdown("## 💡 Improvement Recommendations")
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); 
                    padding: 1.5rem; border-radius: 12px;'>
            <h4>🎯 Focus Areas</h4>
            <ul>
                <li>Review high-confidence mistakes first (>80%)</li>
                <li>Practice specific techniques identified</li>
                <li>Record follow-up videos to track progress</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white;'>
            <h4>📚 Training Tips</h4>
            <ul>
                <li>Work with a coach on flagged techniques</li>
                <li>Use slow-motion replay for analysis</li>
                <li>Compare with professional player videos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🏸 <strong>AI Badminton Coach</strong> | Powered by Computer Vision & Deep Learning</p>
    <p style='font-size: 0.9rem;'>Improve your game with AI-powered analysis</p>
</div>
""", unsafe_allow_html=True)