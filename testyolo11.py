import cv2
import streamlit as st
import numpy as np
from PIL import Image
from ultralytics import YOLO
from collections import Counter

# Load YOLO model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Process and display the detection results
def display_results(image, results):
    boxes = results.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
    scores = results.boxes.conf.cpu().numpy()  # Confidence scores
    labels = results.boxes.cls.cpu().numpy()  # Class indices
    names = results.names  # Class names
    
    detected_objects = []
    
    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Confidence threshold
            x1, y1, x2, y2 = boxes[i].astype(int)
            label = names[int(labels[i])]
            score = scores[i]
            detected_objects.append(label)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return image, detected_objects

# Main Streamlit app
def main():
    st.title("YOLOv11 Object Detection Streamlit App")
    st.sidebar.title("Settings")
    
    model_path = "yolo11n.pt"  # Path to your YOLO model
    model = load_model(model_path)

    # Create the checkbox once
    run_detection = st.sidebar.checkbox("Start/Stop Object Detection", key="detection_control")

    # Open video capture if checkbox is active
    if run_detection:
        cap = cv2.VideoCapture(0)
        st_frame = st.empty()  # Placeholder for video frames
        st_detection_info = st.empty()  # Placeholder for detection information

        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture image.")
                break

            # Run YOLO detection
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
            results = model.predict(frame, imgsz=640)  # Perform detection
            
            # Draw results and collect detected objects
            frame, detected_objects = display_results(frame, results[0])
            
            # Display video feed
            st_frame.image(frame, channels="RGB", use_column_width=True)
            
            # Display detection information
            if detected_objects:
                object_counts = Counter(detected_objects)
                detection_info = "\n".join([f"{obj}: {count}" for obj, count in object_counts.items()])
            else:
                detection_info = "No objects detected."

            st_detection_info.text(detection_info)  # Update detection info text

            # Break the loop if checkbox is unchecked
            if not st.session_state.detection_control:
                break
        
        cap.release()

if __name__ == "__main__":
    main()