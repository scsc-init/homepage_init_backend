# 봇 관련 API 명세서
**최신개정일:** 2025-08-27

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