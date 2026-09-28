from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.chatbot import predict_intent


app = FastAPI(
    title="ShopBot NLP API",
    description="Inference API for the e-commerce customer-support intent classifier.",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Customer message")
    confidence_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional threshold for confidence-aware fallback",
    )


class PredictionResponse(BaseModel):
    text: str
    intent: Optional[str]
    confidence: float
    method: str
    fallback: bool
    normalized_text: str
    tokens: list[str]


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "shopbot-nlp",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> Dict[str, Any]:
    result = predict_intent(request.text)

    fallback = False
    intent = result["intent"]

    if (
        request.confidence_threshold is not None
        and result["confidence"] < request.confidence_threshold
    ):
        intent = None
        fallback = True

    return {
        "text": request.text,
        "intent": intent,
        "confidence": result["confidence"],
        "method": result["method"],
        "fallback": fallback,
        "normalized_text": result["normalized_text"],
        "tokens": result["tokens"],
    }
