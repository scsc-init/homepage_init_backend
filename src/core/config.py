from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

_API_SECRET = os.getenv('API_SECRET')
_SESSION_SECRET = os.getenv('SESSION_SECRET')

def check_api_secret(api_secret: str) -> bool:
    return api_secret == _API_SECRET

def get_session_secret() -> str:
    if not _SESSION_SECRET:
        raise Exception("there is no session secret")
    return _SESSION_SECRET
