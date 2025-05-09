from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

_API_SECRET = os.getenv('API_SECRET')
_SESSION_SECRET = os.getenv('SESSION_SECRET')
_SQLITE_FILE_NAME = os.getenv('SQLITE_FILE_NAME')

def check_api_secret(api_secret: str) -> bool:
    return api_secret == _API_SECRET

def get_session_secret() -> str:
    if not _SESSION_SECRET:
        raise RuntimeError("Missing session secret environment variable")
    return _SESSION_SECRET

def get_sqlite_file_name() -> str:
    if not _SQLITE_FILE_NAME:
        raise RuntimeError("Missing SQLite file name environment variable")
    return _SQLITE_FILE_NAME
