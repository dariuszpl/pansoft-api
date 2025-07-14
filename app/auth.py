from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
import base64
from urllib.parse import urlencode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import SessionLocal
from app.models import User

from app.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login")
def login_with_allegro():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"error": "Brak kodu autoryzacyjnego."})

    async with httpx.AsyncClient() as client:
        try:
            credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            }

            response = await client.post(TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()

            if "access_token" not in token_data:
                return {"error": "Nie udało się pobrać access_token"}

            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token")

            # 👇 Zapytanie o user_id z access_token
            user_info_headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.allegro.public.v1+json"
            }

            user_response = await client.get("https://api.allegro.pl.me/auth/user/me", headers=user_info_headers)
            user_info = user_response.json()

            if "id" not in user_info:
                return {"error": "Nie udało się pobrać user_id"}

            allegro_user_id = user_info["id"]


        except httpx.HTTPStatusError as e:
            return JSONResponse(status_code=e.response.status_code, content={
                "error": f"Nie udało się pobrać tokenu: {str(e)}"
            })
     
    if not allegro_user_id:
        return JSONResponse(status_code=400, content={"error": "Brak user_id w odpowiedzi Allegro"})

    # 🔽 sprawdź czy user już istnieje
    result = await db.execute(select(User).where(User.allegro_id == allegro_user_id))
    user = result.scalars().first()

    if user:
        user.access_token = token_data.get("access_token")
        user.refresh_token = token_data.get("refresh_token")
        user.expires_in = token_data.get("expires_in")
    else:
        user = User(
            allegro_id=allegro_user_id,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in")
        )
        db.add(user)

    await db.commit()

    return JSONResponse(content={
        "message": "✅ Token został zapisany",
        "allegro_id": allegro_user_id
    })
