from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

_FRONTEND_SECRET = os.getenv('FRONTEND_SECRET')
_SESSION_SECRET = os.getenv('SESSION_SECRET')

def check_frontend_secret(frontend_secret: str) -> bool:
    return frontend_secret == _FRONTEND_SECRET

def get_session_secret() -> str:
    if not _SESSION_SECRET:
        raise Exception("there is no session secret")
    return _SESSION_SECRET
