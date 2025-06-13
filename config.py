import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg"}
