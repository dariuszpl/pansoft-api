import os
from dotenv import load_dotenv

load_dotenv() # Załaduj zmienne z pliku .env

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URL = "https://allegro.pl/auth/oauth/authorize"
TOKEN_URL = "https://allegro.pl/auth/oauth/token"
