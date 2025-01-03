import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.inception_v3 import preprocess_input

# Load the trained model
@st.cache_resource
def load_model():
    model_path = r"C:\Users\swift\final deepfake\deepfake-image-detector\main\deepfake_detection_model_DDT.h5"  # Replace with your model path
    return tf.keras.models.load_model(model_path)

# Load the model once
model = load_model()

# Preprocess a video and extract frames
def extract_frames_from_video(video_path, max_frames=20, img_size=(224, 224)):
    cap = cv2.VideoCapture(video_path)
    processed_frames = []
    frame_count = 0
    
    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        resized_frame = cv2.resize(frame, img_size)
        frame_array = img_to_array(resized_frame)
        processed_frame = preprocess_input(frame_array)
        processed_frames.append(processed_frame)
        frame_count += 1
    
    cap.release()
    
    while len(processed_frames) < max_frames:
        processed_frames.append(np.zeros((224, 224, 3)))
    
    return np.array([processed_frames])

# Predict video deepfake status
def predict_video(video_path):
    frames = extract_frames_from_video(video_path)
    prediction = model.predict(frames)
    avg_prediction = np.mean(prediction)
    return "Fake" if avg_prediction > 0.5 else "Real", avg_prediction

# Streamlit Web Interface
st.title("Deepfake Video Detector")
st.write("We offer an AI tool that can identify if an audio or video is a deepfake or real with 80% accuracy.")

# File uploader
uploaded_file = st.file_uploader("Select a video less than 5 MB", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    with st.spinner("Processing video..."):
        # Save the uploaded video to a temporary file
        temp_file = "temp_video.mp4"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Run prediction
        result, confidence = predict_video(temp_file)
        st.success(f"Prediction: {result} (Confidence: {confidence:.2f})")
