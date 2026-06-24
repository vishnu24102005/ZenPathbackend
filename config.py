from dotenv import load_dotenv
import os

load_dotenv()

ALLOWED_ORIGINS = [
    # "http://localhost:5173",
    "https://zen-path-frontend.vercel.app"
]

DATABASE_URL = os.getenv("DATABASE_URL")
