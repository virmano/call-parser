# STO Call Analyzer

A tool for automatic transcription and quality analysis of service center calls using Google Drive, Google Sheets, and Gemini AI.

---

## Requirements

- Python 3.13+
- Poetry
- Google Cloud account
- Gemini API key (Google AI Studio)

---

## Setup

### 1. Clone the repository

```bash
    git clone https://github.com/your-repo/sto-parser.git
    cd sto-parser
```

### 2. Install dependencies

```bash
  poetry install
```

### 3. Google Cloud Console setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `sto-parser`)
3. Enable the following APIs:
   - **Google Drive API**
   - **Google Sheets API**
   - **Gemini API**
4. Go to **IAM & Admin → Service Accounts** → Create Service Account
5. Give it the **Editor** role
6. Go to the service account → **Keys** tab → **Add Key** → **JSON**
7. Download the file and rename it to `google_secret.json`
8. Place `google_secret.json` in the project root folder

### 4. Grant access to Google Drive and Sheets

1. Open your Google Sheet → **Share** → paste the `client_email` from `google_secret.json` → **Editor**
2. Open your Google Drive folder → **Share** → same email → **Editor**

### 5. Get API keys

- **Gemini**: go to [aistudio.google.com](https://aistudio.google.com) → **Get API Key** → **Create API Key**

### 6. Configure environment variables

```bash
  cp .env-example .env
```

Open `.env` and fill in your values:
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
GOOGLE_SECRET_FILE=google_secret.json

**Where to find IDs:**
- **Google Sheets ID**: from the URL `https://docs.google.com/spreadsheets/d/`**`THIS_IS_THE_ID`**`/edit`
- **Google Drive Folder ID**: from the URL `https://drive.google.com/drive/folders/`**`THIS_IS_THE_ID`**

### 7. Prepare Google Drive structure

Create the following folder structure in Google Drive:
Your main folder (GOOGLE_DRIVE_FOLDER_ID)
└── дзвінки/          ← place your .mp3 call recordings here

### 8. Run

```bash
  poetry run python main.py
```

---

## How it works

1. Downloads all `.mp3` files from the `дзвінки` folder on Google Drive
2. Transcribes each file using Gemini AI
3. Analyzes the transcript — evaluates manager quality by criteria
4. Writes results to Google Sheets (skips duplicates automatically)

---

## Project structure
```
sto-parser/
├── main.py                  # Entry point
├── prompts.py               # Prompts for Gemini
├── utils.py                 # Helper functions
├── exceptions.py            # Custom exceptions
├── .env                     # Environment variables (not in git)
├── .env-example             # Example env file
├── google_secret.json       # Google service account key (not in git)
├── pyproject.toml           # Poetry config
├── config/
│   └── settings.py          # Settings and env loading
├── services/
│   └── google_api.py        # Google Drive, Sheets, Gemini services
├── downloads/               # Downloaded mp3 files
└── transcripts/             # Generated transcripts
```
---

---

# STO Call Analyzer (Українська)

Інструмент для автоматичної транскрибації та аналізу якості дзвінків автосервісу за допомогою Google Drive, Google Sheets та Gemini AI.

---

## Вимоги

- Python 3.13+
- Poetry
- Акаунт Google Cloud
- API ключ Gemini (Google AI Studio)
- API ключ Deepgram

---

## Налаштування

### 1. Клонувати репозиторій

```bash
    git clone https://github.com/your-repo/sto-parser.git
    cd sto-parser
```

### 2. Встановити залежності

```bash
    poetry install
```

### 3. Налаштування Google Cloud Console

1. Зайди на [console.cloud.google.com](https://console.cloud.google.com)
2. Створи новий проект (наприклад `sto-parser`)
3. Увімкни наступні API:
   - **Google Drive API**
   - **Google Sheets API**
   - **Gemini API**
4. Зайди в **IAM & Admin → Service Accounts** → Створи сервісний акаунт
5. Дай роль **Editor**
6. Зайди в сервісний акаунт → вкладка **Keys** → **Add Key** → **JSON**
7. Завантаж файл і перейменуй його на `google_secret.json`
8. Поклади `google_secret.json` в кореневу папку проекту

### 4. Надати доступ до Google Drive та Sheets

1. Відкрий Google Sheet → **Share** → встав `client_email` з `google_secret.json` → **Editor**
2. Відкрий папку Google Drive → **Share** → той самий email → **Editor**

### 5. Отримати API ключі

- **Gemini**: зайди на [aistudio.google.com](https://aistudio.google.com) → **Get API Key** → **Create API Key**

### 6. Налаштувати змінні середовища

```bash
  cp .env-example .env
```

Відкрий `.env` і заповни свої значення:
GEMINI_API_KEY=твій_ключ_gemini
DEEPGRAM_API_KEY=твій_ключ_deepgram
GOOGLE_SHEETS_ID=id_твоєї_таблиці
GOOGLE_DRIVE_FOLDER_ID=id_твоєї_папки
GOOGLE_SECRET_FILE=google_secret.json

**Де знайти ID:**
- **Google Sheets ID**: з URL `https://docs.google.com/spreadsheets/d/`**`ЦЕ_І_Є_ID`**`/edit`
- **Google Drive Folder ID**: з URL `https://drive.google.com/drive/folders/`**`ЦЕ_І_Є_ID`**

### 7. Підготувати структуру Google Drive

Створи наступну структуру папок на Google Drive:
Твоя головна папка (GOOGLE_DRIVE_FOLDER_ID)
└── дзвінки/          ← сюди клади .mp3 файли дзвінків

### 8. Запустити

```bash
  poetry run python main.py
```

---

## Як це працює

1. Скачує всі `.mp3` файли з папки `дзвінки` на Google Drive
2. Транскрибує кожен файл через Gemini AI
3. Аналізує транскрипт — оцінює якість роботи менеджера за критеріями
4. Записує результати в Google Sheets (дублікати пропускає автоматично)

---

## Структура проекту
```
sto-parser/
├── main.py                  # Точка входу
├── prompts.py               # Промпти для Gemini
├── utils.py                 # Допоміжні функції
├── exceptions.py            # Кастомні виключення
├── .env                     # Змінні середовища (не в git)
├── .env-example             # Приклад env файлу
├── google_secret.json       # Ключ сервісного акаунту (не в git)
├── pyproject.toml           # Конфігурація Poetry
├── config/
│   └── settings.py          # Налаштування та завантаження env
├── services/
│   └── google_api.py        # Сервіси Google Drive, Sheets, Gemini
├── downloads/               # Скачані mp3 файли
└── transcripts/             # Згенеровані транскрипти
```