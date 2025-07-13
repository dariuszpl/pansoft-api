from fastapi import FastAPI
from auth import router as auth_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Pansoft"}