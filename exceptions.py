class AppServiceException(Exception):
    pass

# Google Drive exceptions
class GoogleDriveError(AppServiceException):
    pass

class FolderNotFoundError(GoogleDriveError):
    pass

# Google Sheets exceptions
class GoogleSheetsError(AppServiceException):
    pass

# Gemini API exceptions
class GeminiAPIError(AppServiceException):
    pass