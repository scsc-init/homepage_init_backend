# 파일 업로드 관련 DB, API 명세서
**최신개정일:** 2025-06-28

# DB 구조

[./common.md](./common.md) `file_metadata` 테이블 참조 

---

## Upload File (파일 업로드)

* **Method**: `POST`
* **URL**: `/api/file/docs/upload`
* **설명**: 인증된 사용자가 파일을 업로드한다. 업로드된 파일 정보는 DB에 저장되며, 고유한 `id(UUID v4)`가 부여된다.

* **Request**:
  * **Content-Type**: `multipart/form-data`
  * **Form Fields**:

    | 필드명  | 타입   | 필수 여부 | 설명                    |
    | ---- | ---- | ----- | --------------------- |
    | file | File | O   | 업로드할 파일 (pdf, pptx, docx) |

* **Response**:

```json
{
  "id": "4c85a8be-59c3-4e1a-bd2f-9f22a0f4d22e",
  "original_filename": "profile.pdf",
  "size": 204832,
  "mime_type": "application/pdf",
  "created_at": "2025-05-21T14:30:00",
  "owner": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
}
```

* **Status Codes**:
  * `201 Created` - 업로드 성공
  * `400 Bad Request` - 파일 누락 또는 유효하지 않은 파일
  * `401 Unauthorized` - 인증 실패 / 로그인 하지 않음
  * `413 Payload Too Large` - 파일 크기 제한 초과

---

## Download File (파일 다운로드)

* **Method**: `GET`
* **URL**: `/api/file/docs/download/:id`
* **설명**: 업로드된 파일를 ID(UUID)로 다운로드한다.

* **Path Parameters**:

  | 파라미터명 | 타입   | 설명               |
  | ----- | ---- | ---------------- |
  | `id`  | TEXT | 파일 UUID (v4 형식) |

* **Response**:
  * **Content-Type**: 파일의 `mime_type` (예: `application/pdf`)
  * 파일 바이너리 스트림

* **예시 요청**:

```http
GET /api/file/download/4c85a8be-59c3-4e1a-bd2f-9f22a0f4d22e
```


* **Status Codes**:

  * `200 OK` - 다운로드 성공
  * `401 Unauthorized` - 인증 실패
  * `404 Not Found` - 존재하지 않는 파일 ID

---

## Upload Image (이미지 업로드)

* **Method**: `POST`
* **URL**: `/api/file/image/upload`
* **설명**: 인증된 사용자가 이미지를 업로드한다. 업로드된 이미지 정보는 DB에 저장되며, 고유한 `id(UUID v4)`가 부여된다.
* **가능한 MIME type**: image/*  
  *(확장자: jpg, jpeg, png, svg, gif, webp)*

* **Request**:
  * **Content-Type**: `multipart/form-data`
  * **Form Fields**:

    | 필드명  | 타입   | 필수 여부 | 설명                    |
    | ---- | ---- | ----- | --------------------- |
    | file | File | O   | 업로드할 이미지 (PNG, JPG 등) |

* **Response**:

```json
{
  "id": "4c85a8be-59c3-4e1a-bd2f-9f22a0f4d22e",
  "original_filename": "profile.jpg",
  "size": 204832,
  "mime_type": "image/jpeg",
  "created_at": "2025-05-21T14:30:00",
  "owner": "b4c9a289323b21a01c3e940f150eb9b8c542587f1abfd8f0e1cc1ffc5e475514",
}
```

* **Status Codes**:
  * `201 Created` - 업로드 성공
  * `400 Bad Request` - 파일 누락 또는 유효하지 않은 이미지
  * `401 Unauthorized` - 인증 실패 / 로그인 하지 않음
  * `413 Payload Too Large` - 파일 크기 제한 초과

---

## Download Image (이미지 다운로드)

* **Method**: `GET`
* **URL**: `/api/file/image/download/:id`
* **설명**: 업로드된 이미지를 ID(UUID)로 다운로드한다.

* **Path Parameters**:

  | 파라미터명 | 타입   | 설명               |
  | ----- | ---- | ---------------- |
  | `id`  | TEXT | 이미지 UUID (v4 형식) |

* **Response**:
  * **Content-Type**: 이미지의 `mime_type` (예: `image/png`, `image/jpeg`)
  * 이미지 바이너리 스트림

* **예시 요청**:

```http
GET /api/image/download/4c85a8be-59c3-4e1a-bd2f-9f22a0f4d22e
```


* **Status Codes**:

  * `200 OK` - 다운로드 성공
  * `401 Unauthorized` - 인증 실패
  * `404 Not Found` - 존재하지 않는 이미지 ID

---