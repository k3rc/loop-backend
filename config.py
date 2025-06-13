import os
SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
ALGORITHM = "HS256"
UPLOAD_DIR = "uploads"
