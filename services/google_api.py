import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config.settings import GOOGLE_SECRET_FILE, GOOGLE_DRIVE_FOLDER_ID

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