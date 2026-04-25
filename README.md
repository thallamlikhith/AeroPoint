# AI Badminton Analyzer: Real-Time Pose & Shot Analysis System

AI Badminton Analyzer is a real-time computer vision system designed to analyze badminton performance using pose estimation, shot classification, and movement tracking. It helps players and coaches gain accurate, AI-driven insights into technique, body mechanics, and gameplay efficiency.

## 🔍 Description (349 characters)
AI Badminton Analyzer uses pose estimation and machine learning to track player movement, classify shots, and detect mistakes. It analyzes joint angles, swing patterns, and footwork, providing instant feedback to help athletes improve accuracy, performance, and overall gameplay.

## 🚀 Features
- Real-time pose detection and tracking  
- Shot classification (smash, clear, drop, drive, net shot)  
- Joint angle and body movement analysis  
- Mistake detection for incorrect technique  
- Automatic visual overlay of skeleton and metrics  
- Streamlit interface for easy use  

## 📂 Project Structure
badminton_ai/
│── streamlit_app.py
│── pipeline.py
│── pose_estimation.py
│── mistake_detector.py
│── ai_models/
│── utils/
│── data/
│── requirements.txt
│── README.md



## 🛠 Installation

### 1. Create Python 3.10 virtual environment
py -3.10 -m venv venv
venv\Scripts\activate

### 2. Install dependencies
pip install -r requirements.txt



## ▶️ Usage
Run the Streamlit app:

streamlit run streamlit_app.py


Run pipeline manually:

python pipeline.py



## 🧠 How It Works
1. Extracts pose keypoints using MediaPipe  
2. Calculates angles, movement vectors, and racket-hand motion  
3. Classifies shots using ML models  
4. Detects mistakes based on biomechanical patterns  
5. Displays results with visual overlays and metrics  

## 📌 Requirements
- Python 3.10
- MediaPipe 0.10.14
- Streamlit UI
- OpenCV for video processing
- Scikit-learn models  

## 👨‍💻 Author
**Bunny Bobbali**  
AI & Data Science Intern  
AI Badminton Analyzer Project
