from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
import os
import httpx
from base64 import b64encode

router = APIRouter()

CLIENT_ID = os.getenv("ALLEGRO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALLEGRO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ALLEGRO_REDIRECT_URI")

@router.get("/auth/login")
def login():
    url = (
        "https://allegro.pl/auth/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )
    return RedirectResponse(url)

@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    basic_auth = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://allegro.pl/auth/oauth/token", data=data, headers=headers)
        if res.status_code != 200:
            return JSONResponse(status_code=res.status_code, content=res.json())
        return res.json() # Zawiera access_token, refresh_token, expires_in itp.