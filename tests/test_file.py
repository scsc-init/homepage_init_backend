import io
import uuid
from pathlib import Path

import pytest
from httpx import HTTPStatusError

from src.core import get_settings


def _upload(client, url: str, headers: dict[str, str], file_tuple):
    stream, filename, content_type = file_tuple
    stream.seek(0)
    files = {"file": (filename, stream.read(), content_type)}
    return client.post(url, headers=headers, files=files)


def test_upload_doc_success(client, api_headers, doc_file):
    settings = get_settings()

    response = _upload(client, "/api/file/docs/upload", api_headers, doc_file)
    response.raise_for_status()

    data = response.json()
    file_path = Path(settings.file_dir) / f"{data['id']}.pdf"
    assert file_path.exists()
    assert file_path.read_bytes() == b"%PDF-1.4 test content"
    assert data["mime_type"] == "application/pdf"


def test_upload_doc_invalid_extension(client, api_headers):
    stream = io.BytesIO(b"plain text")
    files = {"file": ("invalid.txt", stream.read(), "text/plain")}

    response = client.post("/api/file/docs/upload", headers=api_headers, files=files)

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert list(Path(get_settings().file_dir).iterdir()) == []


def test_upload_doc_payload_too_large(client, api_headers):
    limit = get_settings().file_max_size + 1
    stream = io.BytesIO(b"x" * limit)
    files = {"file": ("large.pdf", stream.read(), "application/pdf")}

    response = client.post("/api/file/docs/upload", headers=api_headers, files=files)

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert list(Path(get_settings().file_dir).iterdir()) == []


def test_upload_doc_requires_auth(client, api_headers, set_current_user, doc_file):
    set_current_user(None)

    response = _upload(client, "/api/file/docs/upload", api_headers, doc_file)

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert list(Path(get_settings().file_dir).iterdir()) == []


def test_download_doc_success(client, api_headers, doc_file):
    upload_response = _upload(client, "/api/file/docs/upload", api_headers, doc_file)
    upload_response.raise_for_status()
    file_id = upload_response.json()["id"]

    response = client.get(f"/api/file/docs/download/{file_id}", headers=api_headers)
    response.raise_for_status()

    assert response.content == b"%PDF-1.4 test content"
    assert response.headers["content-type"] == "application/pdf"


def test_download_doc_not_found(client, api_headers):
    response = client.get(
        f"/api/file/docs/download/{uuid.uuid4()}", headers=api_headers
    )

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert response.headers["content-type"].startswith("application/json")


def test_download_doc_requires_api_secret(client, set_current_user):
    set_current_user(None)

    response = client.get(f"/api/file/docs/download/{uuid.uuid4()}")

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()


def test_upload_image_success(client, api_headers, image_file):
    settings = get_settings()

    response = _upload(client, "/api/file/image/upload", api_headers, image_file)
    response.raise_for_status()

    data = response.json()
    file_path = Path(settings.image_dir) / f"{data['id']}.png"
    assert file_path.exists()
    assert file_path.read_bytes() == b"binary image"
    assert data["mime_type"].startswith("image/")


def test_upload_image_invalid_extension(client, api_headers):
    stream = io.BytesIO(b"data")
    files = {"file": ("invalid.bmp", stream.read(), "image/bmp")}

    response = client.post("/api/file/image/upload", headers=api_headers, files=files)

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert list(Path(get_settings().image_dir).iterdir()) == []


def test_upload_image_requires_auth(client, api_headers, set_current_user, image_file):
    set_current_user(None)

    response = _upload(client, "/api/file/image/upload", api_headers, image_file)

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert list(Path(get_settings().image_dir).iterdir()) == []


def test_download_image_success(client, api_headers, image_file):
    upload_response = _upload(client, "/api/file/image/upload", api_headers, image_file)
    upload_response.raise_for_status()
    file_id = upload_response.json()["id"]

    response = client.get(f"/api/file/image/download/{file_id}", headers=api_headers)
    response.raise_for_status()

    assert response.content == b"binary image"
    assert response.headers["content-type"].startswith("image/")


def test_download_image_not_found(client, api_headers):
    response = client.get(
        f"/api/file/image/download/{uuid.uuid4()}", headers=api_headers
    )

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
    assert response.headers["content-type"].startswith("application/json")


def test_download_image_requires_api_secret(client, set_current_user):
    set_current_user(None)

    response = client.get(f"/api/file/image/download/{uuid.uuid4()}")

    with pytest.raises(HTTPStatusError):
        response.raise_for_status()
