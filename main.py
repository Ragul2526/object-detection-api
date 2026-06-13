from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, Response
from detector import detect_object
import io
from PIL import Image
app = FastAPI(
    title= "Object Detection API",
    description= "Upload an image and get detected objects using YOLO",
    version = "1.0.3"
    )

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Object Detection API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: #1a1a2e;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: #16213e;
            padding: 40px;
            border-radius: 12px;
            width: 600px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        h1 { color: #00d4ff; margin-bottom: 8px; }
        p  { color: #888; margin-bottom: 30px; }
        
        .upload-area {
            border: 2px dashed #00d4ff;
            border-radius: 8px;
            padding: 40px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .upload-area:hover { background: rgba(0,212,255,0.05); }
        .upload-area input { display: none; }
        .upload-area label { cursor: pointer; color: #00d4ff; }
        
        #preview {
            max-width: 100%;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        button {
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            padding: 12px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-bottom: 20px;
            transition: opacity 0.3s;
        }
        button:hover   { opacity: 0.8; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        #result-image {
            max-width: 100%;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        #detections {
            text-align: left;
            background: #0f3460;
            border-radius: 8px;
            padding: 16px;
            display: none;
        }
        
        .detection-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .detection-item:last-child { border-bottom: none; }
        .label { font-weight: bold; color: #00d4ff; }
        .confidence { color: #888; }
        
        #status { color: #888; margin: 10px 0; }
        #download { display: none; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔍 Object Detection</h1>
    <p>Upload an image to detect objects using YOLOv8</p>
    
    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <input type="file" id="fileInput" accept="image/*" onchange="previewImage(this)">
        <label>📁 Click to upload image</label>
        <p style="color:#555; margin-top:8px; font-size:12px;">JPG, PNG supported</p>
    </div>
    
    <img id="preview" alt="preview"/>
    
    <button id="detectBtn" onclick="detect()" disabled>Detect Objects</button>
    
    <p id="status"></p>
    
    <img id="result-image" alt="result"/>
    
    <div id="detections"></div>
    
    <a id="download" download="detected.jpg">
        <button style="background:#2ecc71; margin-top:10px;">
            ⬇ Download Result
        </button>
    </a>
</div>

<script>
    let selectedFile = null;

    function previewImage(input) {
        selectedFile = input.files[0];
        if (!selectedFile) return;
        
        const reader = new FileReader();
        reader.onload = e => {
            const preview = document.getElementById('preview');
            preview.src = e.target.result;
            preview.style.display = 'block';
            document.getElementById('detectBtn').disabled = false;
        };
        reader.readAsDataURL(selectedFile);
    }

    async function detect() {
        if (!selectedFile) return;
        
        const btn    = document.getElementById('detectBtn');
        const status = document.getElementById('status');
        
        btn.disabled = true;
        btn.textContent = 'Detecting...';
        status.textContent = 'Running detection, please wait...';
        
        document.getElementById('result-image').style.display = 'none';
        document.getElementById('detections').style.display   = 'none';
        document.getElementById('download').style.display     = 'none';

        try {
            // get annotated image
            const formData1 = new FormData();
            formData1.append('file', selectedFile);
            const imgResponse = await fetch('/detect/image', {
                method: 'POST',
                body: formData1
            });
            const imgBlob = await imgResponse.blob();
            const imgUrl  = URL.createObjectURL(imgBlob);
            
            // get detections JSON
            const formData2 = new FormData();
            formData2.append('file', selectedFile);
            const jsonResponse = await fetch('/detect/json', {
                method: 'POST',
                body: formData2
            });
            const data = await jsonResponse.json();
            
            // show annotated image
            const resultImg = document.getElementById('result-image');
            resultImg.src = imgUrl;
            resultImg.style.display = 'block';
            
            // show detections list
            const detectionsDiv = document.getElementById('detections');
            if (data.detections.length === 0) {
                detectionsDiv.innerHTML = '<p style="color:#888">No objects detected</p>';
            } else {
                detectionsDiv.innerHTML = `
                    <p style="margin-bottom:12px; color:#888">
                        Found <strong style="color:white">${data.total_objects}</strong> object(s)
                    </p>
                    ${data.detections.map(d => `
                        <div class="detection-item">
                            <span class="label">${d.label}</span>
                            <span class="confidence">${(d.confidence * 100).toFixed(0)}% confidence</span>
                        </div>
                    `).join('')}
                `;
            }
            detectionsDiv.style.display = 'block';
            
            // download button
            const downloadLink = document.getElementById('download');
            downloadLink.href = imgUrl;
            downloadLink.style.display = 'block';
            
            status.textContent = '';
            
        } catch (err) {
            status.textContent = 'Error: ' + err.message;
        }
        
        btn.disabled    = false;
        btn.textContent = 'Detect Objects';
    }
</script>
</body>
</html>
"""

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
    