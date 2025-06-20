from fastapi import HTTPException, Request, UploadFile, File
import csv
import io
from src.model import User
from src.core import get_settings
from datetime import datetime



def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()


def get_user(request: Request) -> User:
    user = request.state.user
    if not user: raise HTTPException(401, detail="Not logged in")
    return user


async def process_standby_user(encoding: str, file: UploadFile = File(...)) -> list[tuple[int, str, str]]:
    contents = await file.read()
    if len(contents) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")
    decoded = contents.decode(encoding)
    f = io.StringIO(decoded)
    lines = f.readlines()
    trimmed_lines = lines[4:-1]
    trimmed_csv = io.StringIO("".join(trimmed_lines))
    reader = csv.DictReader(trimmed_csv)
    result = []
    for line in reader:
        result.append((int(str(line["입금액"]).replace(',', '')), line["거래일시"], line["보낸분/받는분"]))
    return result
