import os
import gspread
from google import genai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config.settings import GOOGLE_SECRET_FILE
from exceptions import (
    GoogleDriveError, FolderNotFoundError,
    GoogleSheetsError, GeminiAPIError
)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
]


class GoogleDiskService:
    def __init__(self):
        try:
            creds = Credentials.from_service_account_file(
                GOOGLE_SECRET_FILE,
                scopes=SCOPES
            )
            self.service = build("drive", "v3", credentials=creds)
        except Exception as e:
            raise GoogleDriveError(f"Failed to initialize Google Drive service: {e}")

    def get_folder_id_by_name(self, name: str, parent_id: str) -> str | None:
        try:
            response = self.service.files().list(
                q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false",
                fields="files(id, name)"
            ).execute()
            files = response.get("files", [])
            if files:
                return files[0]["id"]
            raise FolderNotFoundError(f"Folder '{name}' not found in parent '{parent_id}'")
        except FolderNotFoundError:
            raise
        except Exception as e:
            raise GoogleDriveError(f"Failed to get folder '{name}': {e}")

    def list_mp3_files(self, folder_id: str) -> list:
        try:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and mimeType='audio/mpeg' and trashed=false",
                fields="files(id, name)"
            ).execute()
            return response.get("files", [])
        except Exception as e:
            raise GoogleDriveError(f"Failed to list mp3 files in folder '{folder_id}': {e}")

    def list_files(self, folder_id: str) -> list:
        try:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType)"
            ).execute()
            return response.get("files", [])
        except Exception as e:
            raise GoogleDriveError(f"Failed to list files in folder '{folder_id}': {e}")

    def download_file(self, file_id: str, file_name: str, save_folder: str) -> str:
        try:
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
        except Exception as e:
            raise GoogleDriveError(f"Failed to download file '{file_name}': {e}")

    def download_all_mp3_files(self, folder_id: str, save_folder: str) -> list[str]:
        try:
            files = self.list_mp3_files(folder_id)
            downloaded = []

            for file in files:
                path = self.download_file(file["id"], file["name"], save_folder)
                downloaded.append(path)

            print(f"{len(downloaded)} files downloaded")
            return downloaded
        except GoogleDriveError:
            raise
        except Exception as e:
            raise GoogleDriveError(f"Failed to download all mp3 files: {e}")


class GoogleSheetsService:
    def __init__(self, sheet_id):
        try:
            creds = Credentials.from_service_account_file(
                GOOGLE_SECRET_FILE,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(sheet_id).sheet1
        except Exception as e:
            raise GoogleSheetsError(f"Failed to initialize Google Sheets service: {e}")

    def get_all_rows(self) -> list:
        try:
            return self.sheet.get_all_values()
        except Exception as e:
            raise GoogleSheetsError(f"Failed to get all rows: {e}")

    def append_row(self, row: list) -> None:
        try:
            self.sheet.append_row(row)
        except Exception as e:
            raise GoogleSheetsError(f"Failed to append row: {e}")

    def update_cell(self, row: int, col: int, value) -> None:
        try:
            self.sheet.update_cell(row, col, value)
        except Exception as e:
            raise GoogleSheetsError(f"Failed to update cell ({row}, {col}): {e}")

    def get_headers(self) -> list:
        try:
            return self.sheet.row_values(1)
        except Exception as e:
            raise GoogleSheetsError(f"Failed to get headers: {e}")

    def delete_row(self, row_index: int) -> None:
        try:
            self.sheet.delete_rows(row_index)
        except Exception as e:
            raise GoogleSheetsError(f"Failed to delete row {row_index}: {e}")

    def update_row(self, row_index: int, values: list) -> None:
        try:
            self.sheet.update(f"A{row_index}", [values])
        except Exception as e:
            raise GoogleSheetsError(f"Failed to update row {row_index}: {e}")

    def find_row_by_value(self, value: str, col: int = 1) -> int | None:
        try:
            cell = self.sheet.find(value, in_column=col)
            if cell:
                return cell.row
            return None
        except Exception as e:
            raise GoogleSheetsError(f"Failed to find row by value '{value}': {e}")


class GeminiAPIService:
    def __init__(self, api_key: str = None):
        try:
            if not api_key:
                from config.settings import GEMINI_API_KEY
                api_key = GEMINI_API_KEY
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise GeminiAPIError(f"Failed to initialize Gemini API service: {e}")

    def process_file_with_prompt(self, file_path: str, prompt: str, model_name: str = "gemini-3.1-flash-lite") -> str:
        if not os.path.exists(file_path):
            raise GeminiAPIError(f"File not found: {file_path}")

        uploaded_file = None
        try:
            print(f"1. Uploading file '{file_path}' to Gemini...")
            uploaded_file = self.client.files.upload(file=file_path)
            print("File uploaded successfully.")

            print(f"2. Sending request to {model_name}...")
            response = self.client.models.generate_content(
                model=model_name,
                contents=[uploaded_file, prompt]
            )
            return response.text
        except Exception as e:
            raise GeminiAPIError(f"Failed to process file with Gemini: {e}")
        finally:
            if uploaded_file:
                try:
                    print("3. Removing file from Gemini File API...")
                    self.client.files.delete(name=uploaded_file.name)
                except Exception as e:
                    print(f"Warning: Could not delete file {uploaded_file.name}: {e}")

    def process_prompt(self, prompt: str, model_name: str = "gemini-3.1-flash-lite") -> str:
        try:
            print(f"Sending prompt to {model_name}...")
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise GeminiAPIError(f"Failed to process prompt with Gemini: {e}")