from fastapi import FastAPI

from app.agent_router import route_message

from app.schemas import ClassificationRequest, ClassificationResponse

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "AI Classifier Backend działa"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.post("/classify", response_model=ClassificationResponse)
def classify(request: ClassificationRequest):
    return route_message(request.text)