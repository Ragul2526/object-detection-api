from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, Response
from detector import detect_object

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
    detection, _ = detect_object(img_bytes)
    
    return JSONResponse(content={
        "filename" : file.filename,
        "total_objects" : len(detection),
        "detections" : detection
        })

@app.post("/detect/image")

async def detect_image(file : UploadFile = File(...)):
    img_bytes = await file.read()
    _, annotated_bytes = detect_object(img_bytes)
    
    return Response(
        content= annotated_bytes,
        media_type= "image/jpeg"
                    )

@app.post("detect")
async def detect_both( file : UploadFile = File(...)):
    img_bytes = await file.read()
    detection, annotated_bytes = detect_object(img_bytes)
    
    return JSONResponse(content={
        "filename" : file.filename,
        "total_objects" : len(detection),
        "detections" : detection,
        "message" : "Use /detect/image endpoint to get annotated image"
        })
    