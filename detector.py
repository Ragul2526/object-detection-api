from ultralytics import YOLO
import cv2
import numpy as np


model = YOLO("yolov8n.pt") #the default model is yolo26n, the one used here is smallest and fastest
def detect_object(image : bytes):
    nparr = np.frombuffer(image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    result = model(img)
    
    detect = []
    for r in result:
        for box in r.boxes:
            detect.append({
                "label": r.names[int(box.cls)],
                "confidence" : round(float(box.conf),2),
                "bbox": {
                    "x1" : int(box.xyxy[0][0]),
                    "y1" : int(box.xyxy[0][1]),
                    "x2" : int(box.xyxy[0][2]),
                    "y2" : int(box.xyxy[0][3]),
                    }
                
               } )
    annotated = result[0].plot()
    _, buffer = cv2.imencode(".jpg",annotated)
    annotated_bytes = buffer.tobytes()
     
    return detect, annotated_bytes