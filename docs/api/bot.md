# 봇 관련 API 명세서
**최신개정일:** 2026-09-20

# API 구조

## 봇 관련 API(/api/bot)

- 봇 정보를 관리하는 API
- 도커를 통해 함께 실행되는 봇의 정보를 전달한다. 

---

## Get Discord Invite

- **Method**: `GET`
- **URL**: `/api/bot/discord/general/get_invite`

- **Response**:
```json
{"result": "invitation-url"}
```
- **Status Codes**:
  - `500 Internal Server Error`: 예기치 못한 오류
  - `504 Gateway Timeout`: 봇이 시간 안에 응답하지 않음

---

## Send Developer Contact

- **Method**: `POST`
- **URL**: `/api/bot/discord/developer/contact`
- 홈페이지에서 접수한 개발자 문의를 RabbitMQ를 통해 설정된 디스코드 채널로 전송한다.

- **Request Body** (JSON):

```json
{
  "name": "홍길동",
  "email": "example@snu.ac.kr",
  "title": "문의 제목",
  "content": "문의 내용"
}
```

- **Status Codes**:
  - `201 Created`: 문의 전송 요청 성공
  - `422 Unprocessable Entity`: 요청값 형식 또는 길이가 올바르지 않음
  - `503 Service Unavailable`: RabbitMQ가 비활성화됨

---

## Send Message to ID

- **Method**: `POST`
- **URL**: `/api/bot/discord/general/send_message_to_id`
- rabbitmq를 통해 봇에게 1002번 액션 코드로 명령을 보낸다. 자세한 사항은 봇 레포지토리 참고.

- **Request Body** (JSON):
```json
{
  "id": "",
  "content": ""
}
```

- **Status Codes**:
  - `201 Created`

---

## Get Status

- **Method**: `GET`
- **URL**: `/api/bot/discord/status`
- 봇에 `/status` 경로로 요청을 보내 봇의 로그인 여부를 확인한다. 

- **Response**:
```json
{"logged_in": true}
```
- **Status Codes**:
  - `200 OK`
  - `400 Bad Request`: 봇이 정상적으로 응답하지 않음
  - `504 Gateway Timeout`: 봇이 시간 안에 응답하지 않음

---

## Login

- **Method**: `POST`
- **URL**: `/api/bot/discord/login`
- 봇에 `/login` 경로로 요청을 보내 봇을 로그인시킨다. 

- **Status Codes**:
  - `204 No Content`
  - `400 Bad Request`: 봇이 정상적으로 응답하지 않음
  - `504 Gateway Timeout`: 봇이 시간 안에 응답하지 않음

---