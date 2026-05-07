from fastapi import FastAPI

from app.classifier import classify_text
from app.schemas import ClassificationRequest, ClassificationResponse

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "AI Classifier Backend działa"
    }


@app.post("/classify", response_model=ClassificationResponse)
def classify(request: ClassificationRequest):
    return classify_text(request.text)