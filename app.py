from PIL import Image
from ultralytics import YOLO
import cv2
import numpy as np
import gradio as gr

model = YOLO("yolov8.pt")

def detect(img):
    img = np.array(img)
    results = model(img)
    
    detections = []
    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls)]
            conf  = round(float(box.conf), 2)
            detections.append(f"{label} — {int(conf*100)}% confidence")
    
    
    annotated = Image.fromarray(results[0].plot())
    
    
    if detections:
        text = f"Found {len(detections)} object(s):\n\n" + "\n".join(detections)
    else:
        text = "No objects detected"
    
    return annotated, text

demo = gr.Interface( fn = detect, 
                    inputs = gr.Image(type="pil", label = "Upload image") ,
                    outputs = [
                        gr.Image(type = "pil", label = "Detected Objects" ),
                        gr.Textbox(label = "Detection", lines = 10)
                        
                        ],
                    title = "Object Detection",
                    description = "Upload any image to detect objects using YOLOv8. Detects 80 object classes including people, vehicles, animals and more.",
                    examples = [],
                    theme = gr.themes.Soft()
                    )
demo.launch(server_name="0.0.0.0", server_port=7860)