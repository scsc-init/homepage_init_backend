# homepage_init_backend

2025년 4월 30일에 시작한 SCSC 홈페이지 제작 프로젝트의 백엔드 부분입니다. 이 문서는 백엔드 실행 방법과 프로젝트 구조를 다룹니다.


## 실행 방법

### conda 환경을 설정합니다. 
```bash
conda env update -n my_env --file environment.yml
```

### .env 파일을 작성합니다. 
- API_SECRET: api 요청 시 코드가 맞지 않으면 401 상태 코드로 거절
- SESSION_SECRET: 로그인 세션 관련 비밀 코드
- SQLITE_FILE_NAME: sqlite3 DB 파일 경로
```
API_SECRET="some-secret-code"
SESSION_SECRET="some-session-secret"
SQLITE_FILE_NAME="dbname.db"
```

### 실행
```bash
fastapi run main.py --host YOUR_HOST --port YOUR_PORT
```

### 기타

- 실행 명령어 상세 설명

```bash
fastapi run --help
```

- 개발 중 실행 명령어

```bash
fastapi dev main.py
```

- 개발 중 https 실행 명령어

Generate self-signed certs:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Run FastAPI dev server with HTTPS:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```


## 프로젝트 구조

### /(root)
- main.py
- requirements.txt: 파이썬 패키지 정보
- environment.yml: conda 환경 정보
- .env: 환경 변수 정보


### /docs
API 문서를 포함합니다.


### /src
main.py를 제외한 모든 코드를 포함합니다. 

#### /auth
로그인 관련 로직을 포함합니다.

#### /core
환경변수 등 프로젝트 전반에 필요한 로직을 포함합니다.

#### /db
SQLite3 DB 연결 관련 로직을 포함합니다.

#### /middleware
미들웨어를 포함합니다.

#### /model
DB 테이블 관련 로직을 포함합니다. 

#### /routes
라우터를 포함합니다. `root.py`는 모든 라우터를 포함한 루트 라우터를 정의합니다. 