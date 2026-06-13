from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, Response
from detector import detect_object
import io
from PIL import Image
app = FastAPI(
    title= "Object Detection API",
    description= "Upload an image and get detected objects using YOLO",
    version = "1.0.0"
    )

@app.get("/")
def home():
    return {"message" : "Object detection API is running"}

@app.post("/detect/json")

async def detect_json(file : UploadFile = File(...)):
    img_bytes = await file.read()
    #Since in render its taking longer so trying to reduce image size 
    img = Image.open(io.BytesIO(img_bytes))
    img.thumbnail((640, 640))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    detection, _ = detect_object(img_bytes)
    
    return JSONResponse(content={
        "filename" : file.filename,
        "total_objects" : len(detection),
        "detections" : detection
        })

@app.post("/detect/image")

async def detect_image(file : UploadFile = File(...)):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes))
    img.thumbnail((640, 640))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    detection, _ = detect_object(img_bytes)
    _, annotated_bytes = detect_object(img_bytes)
    
    return Response(
        content= annotated_bytes,
        media_type= "image/jpeg"
                    )

@app.post("detect")
async def detect_both( file : UploadFile = File(...)):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes))
    img.thumbnail((640, 640))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    detection, _ = detect_object(img_bytes)
    detection, annotated_bytes = detect_object(img_bytes)
    
    return JSONResponse(content={
        "filename" : file.filename,
        "total_objects" : len(detection),
        "detections" : detection,
        "message" : "Use /detect/image endpoint to get annotated image"
        })
    