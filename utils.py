import json
from config.settings import SCORE_FIELDS


def parse_phone(file_name: str) -> str:
    try:
        parts = file_name.replace(".mp3", "").split("_")
        phone = parts[2]

        return phone
    except Exception:
        return ''


def build_row(file_name: str, data: dict, transcription: str) -> list:
    score = sum(data.get(field, 0) for field in SCORE_FIELDS)

    return [
        transcription,                              # Транскрипція
        data.get("тип_звернення", ""),              # Тип звернення
        parse_phone(file_name),                     # Номер телефону
        "",                                         # Філія (порожньо — невідомо)
        "",                                         # Менеджер (порожньо — невідомо)
        data.get("представлення", 0),               # Представлення
        data.get("кузов_автомобіля", 0),            # Кузов
        data.get("рік_автомобіля", 0),              # Рік
        data.get("пробіг", 0),                      # Пробіг
        data.get("комплексна_діагностика", 0),      # Діагностика
        data.get("попередні_роботи", 0),            # Попередні роботи
        data.get("запис_на_сервіс", ""),            # Запис на сервіс
        data.get("прощання", 0),                    # Прощання
        data.get("робота_з_топ100", ""),            # Робота з топ 100
        data.get("дотримання_інструкцій", ""),      # Дотримання інструкцій
        data.get("недотримані_рекомендації", ""),   # Недотримані рекомендації
        data.get("результат", ""),                  # Результат
        score,                                      # Оцінка
        data.get("запчастини", ""),                 # Запчастини
        data.get("коментар", ""),                   # Коментар
    ]


def parse_analyze(analyze_text: str) -> dict:
    try:
        clean = analyze_text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)
    except Exception as e:
        print(f"Помилка парсингу JSON: {e}")
        return {}
