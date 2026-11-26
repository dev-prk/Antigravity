FROM python:3.11-slim
WORKDIR /service
RUN pip install --no-cache-dir fastapi uvicorn python-multipart numpy requests
COPY ../../src/speech.py ./speech.py
EXPOSE 8890
CMD ["python", "-c", "import uvicorn; from fastapi import FastAPI, UploadFile, File; from speech import SpeechPipeline; app=FastAPI(); sp=SpeechPipeline();\n@app.post('/transcribe')\nasync def tr(file: UploadFile = File(...)):\n out=sp.transcribe_asr(await file.read()); return {'text': out['transcript']}\nuvicorn.run(app, host='0.0.0.0', port=8890)"]
