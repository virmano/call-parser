from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_SECRET_FILE = os.getenv("GOOGLE_SECRET_FILE", "google_secret.json")

SCORE_FIELDS = [
    "представлення",
    "кузов_автомобіля",
    "рік_автомобіля",
    "пробіг",
    "комплексна_діагностика",
    "попередні_роботи",
    "прощання"
]