import os
from pathlib import Path

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/RAJNEETI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = Path(__file__).resolve().parent
    HTML_DIR = BASE_DIR / 'data/html_files'
    JSON_DIR = BASE_DIR / 'data/json_output'
    
    def __init__(self):
        self.HTML_DIR.mkdir(parents=True, exist_ok=True)
        self.JSON_DIR.mkdir(parents=True, exist_ok=True)