from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class SuggestRequest(BaseModel):
    text: str

@router.post("/suggest")
def suggest(req: SuggestRequest):
    res = requests.post(
        "https://api.languagetool.org/v2/check",
        data={"text": req.text, "language": "en-US"}
    )
    matches = res.json().get("matches", [])
    suggestions = [
        {
            "message": m["message"],
            "offset": m["offset"],
            "length": m["length"]  # ← include the length
        }
        for m in matches
    ]
    return suggestions
