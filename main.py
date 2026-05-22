import os
from config.settings import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_SHEETS_ID
from prompts import TRANSCRIPTION_PROMPT, ANALYZE_PROMPT
from services.google_api import GoogleDiskService, GeminiAPIService, GoogleSheetsService
from utils import build_row, parse_analyze

DOWNLOADS_FOLDER = "downloads"
TRANSCRIPTS_FOLDER = "transcripts"

def main():
    drive = GoogleDiskService()
    gemini = GeminiAPIService()
    sheets = GoogleSheetsService(GOOGLE_SHEETS_ID)

    print(" --- Getting calls folder --- ")
    folder_id = drive.get_folder_id_by_name("дзвінки", GOOGLE_DRIVE_FOLDER_ID)
    print(f"Folder found: {folder_id}")

    print("\n--- Downloading files ---")
    file_paths = drive.download_all_mp3_files(folder_id, DOWNLOADS_FOLDER)

    print("\n--- Transcribing and analyze ---")
    os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        transcript_path = os.path.join(TRANSCRIPTS_FOLDER, file_name.replace(".mp3", ".txt"))

        if os.path.exists(transcript_path):
            print(f"Transcribing already done: {file_name}")
            continue
        else:
            print(f"\nTranscribing: {file_name}")
            try:
                transcript = gemini.process_file_with_prompt(file_path, TRANSCRIPTION_PROMPT)
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                print(f"Saved at: {transcript_path}")
            except Exception as e:
                print(f"Error on transcribing {file_name}: {e}")
                continue

        print(f"Analyze: {file_name}")
        try:
            prompt = ANALYZE_PROMPT.replace("{TRANSCRIPT}", transcript)
            analyze_text = gemini.process_prompt(prompt)
            data = parse_analyze(analyze_text)

            if data:
                row = build_row(file_name, data, transcript)
                sheets.append_row(row)
                print(f"Write data to table: {file_name}")
            else:
                print(f"Error in writing data {file_name}")

        except Exception as e:
            print(f"Analyze problem {file_name}: {e}")
            continue

    print("\n=== Done ===")


if __name__ == "__main__":
    main()