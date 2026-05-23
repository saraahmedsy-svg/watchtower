import os
import requests
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

NIMBLE_API_KEY = os.getenv("NIMBLE_API_KEY")

@app.get("/")
def root():
    return {"message": "Watchtower backend running"}

@app.get("/scrape")
def scrape(url: str):

    response = requests.post(
        "https://api.nimbleway.com/api/v1/",
        headers={
            "Authorization": f"Bearer {NIMBLE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "url": url,
            "render": True
        }
    )

    data = response.json()

    return {
        "status": "success",
        "data": data
    }