FROM python:3.11-slim
WORKDIR /service
RUN pip install --no-cache-dir fastapi uvicorn numpy requests
COPY ../../src/speech.py ./speech.py
EXPOSE 8880
CMD ["python", "-c", "import uvicorn; from fastapi import FastAPI, Response; from pydantic import BaseModel; from speech import SpeechPipeline; app=FastAPI(); sp=SpeechPipeline();\nclass Req(BaseModel):\n text: str\n voice: str='aarav'\n language: str='English'\n@app.post('/synthesize')\ndef syn(r: Req):\n wav,_=sp.synthesize_tts(r.text, r.voice, r.language); return Response(content=wav, media_type='audio/wav')\nuvicorn.run(app, host='0.0.0.0', port=8880)"]
