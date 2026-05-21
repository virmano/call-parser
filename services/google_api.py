import os
import gspread
from google import genai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config.settings import GOOGLE_SECRET_FILE

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]

class GoogleDiskService:
    def __init__(self):
        creds = Credentials.from_service_account_file(
            GOOGLE_SECRET_FILE,
            scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=creds)

    def get_folder_id_by_name(self, name: str, parent_id: str) -> str | None:
        response = self.service.files().list(
            q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false",
            fields="files(id, name)"
        ).execute()
        files = response.get("files", [])
        print(files)
        if files:
            return files[0]["id"]
        return None

    def list_mp3_files(self, folder_id: str) -> list:
        response = self.service.files().list(
            q=f"'{folder_id}' in parents and mimeType='audio/mpeg' and trashed=false",
            fields="files(id, name)"
        ).execute()
        print(response)
        return response.get("files", [])

    def list_files(self, folder_id: str) -> list:
        response = self.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)"
        ).execute()
        return response.get("files", [])

    def download_file(self, file_id: str, file_name: str, save_folder: str) -> str:
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, file_name)

        if os.path.exists(file_path):
            print(f"Already exists: {file_name}")
            return file_path

        request = self.service.files().get_media(fileId=file_id)

        with open(file_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name}: {int(status.progress() * 100)}%")

        return file_path

    def download_all_mp3_files(self, folder_id: str, save_folder: str) -> list[str]:
        files = self.list_mp3_files(folder_id)
        downloaded = []

        for file in files:
            path = self.download_file(file["id"], file["name"], save_folder)
            downloaded.append(path)

        print(f"{len(downloaded)} files downloaded")
        return downloaded


class GoogleSheetsService:
    def __init__(self, sheet_id):
        creds = Credentials.from_service_account_file(
            GOOGLE_SECRET_FILE,
            scopes=SCOPES
        )
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def get_all_rows(self) -> list:
        return self.sheet.get_all_values()

    def append_row(self, row: list) -> None:
        self.sheet.append_row(row)

    def update_cell(self, row: int, col: int, value) -> None:
        self.sheet.update_cell(row, col, value)

    def get_headers(self) -> list:
        return self.sheet.row_values(1)

    def delete_row(self, row_index: int) -> None:
        self.sheet.delete_rows(row_index)

    def update_row(self, row_index: int, values: list) -> None:
        self.sheet.update(f"A{row_index}", [values])

    def find_row_by_value(self, value: str, col: int = 1) -> int | None:
        cell = self.sheet.find(value, in_column=col)
        if cell:
            return cell.row
        return None


class GeminiAPIService:
    def __init__(self, api_key: str = None):

        self.client = genai.Client(api_key=api_key)

    def process_file_with_prompt(self, file_path: str, prompt: str, model_name: str = "gemini-2.5-flash") -> str:

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"1. Uploading file '{file_path}' to Gemini...")

        uploaded_file = self.client.files.upload(file=file_path)
        print(f"File was uploaded successfully.")

        try:
            print(f"2. Sending request to {model_name}...")

            response = self.client.models.generate_content(
                model=model_name,
                contents=[uploaded_file, prompt]
            )

            result_text = response.text
            return result_text

        finally:
            print("3. Remove used file from Gemini File API...")
            self.client.files.delete(name=uploaded_file.name)

    def process_prompt(self, prompt: str, model_name: str = "gemini-2.5-flash") -> str:
        print(f"Sending prompt to {model_name}...")
        try:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error with Gemini: {e}")
            raise