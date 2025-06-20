# homepage_init_backend

2025년 4월 30일에 시작한 SCSC 홈페이지 제작 프로젝트의 백엔드 부분입니다. 이 문서는 백엔드 실행 방법과 프로젝트 구조를 다룹니다.

> 최종개정일: 2025-06-18  

## .env 파일 형식

.env 파일은 반드시 root에 위치해야 하며 아래 형식으로 작성합니다. 

```env
API_SECRET="some-secret-code"
JWT_SECRET="some-session-secret"
JWT_VALID_SECONDS=3600
SQLITE_FILENAME="db/YOUR_DB_FILENAME.db"
IMAGE_DIR="static/image/photo/"
IMAGE_MAX_SIZE=10000000
FILE_DIR="download/"
FILE_MAX_SIZE=10000000
ARTICLE_DIR="static/article/"
USER_CHECK=TRUE
ENROLLMENT_FEE=300000
CORS_ALL_ACCEPT=FALSE
```

| Key Name             | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `API_SECRET`         | API 요청 시 검증에 사용되는 비밀 코드. 일치하지 않으면 401 반환  |
| `JWT_SECRET`         | 로그인 관련 JWT를 암호화하거나 검증하는 데 사용하는 비밀 키          |
| `JWT_VALID_SECONDS`  | 로그인 관련 JWT 유효 시간(초)          |
| `SQLITE_FILENAME`    | SQLite3 데이터베이스 파일의 경로 또는 파일 이름                  |
| `IMAGE_DIR`          | 이미지 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `IMAGE_MAX_SIZE`     | 이미지 최대 용량(바이트) |
| `FILE_DIR`           | 파일 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `FILE_MAX_SIZE`      | 파일 최대 용량(바이트) |
| `ARTICLE_DIR`        | 글 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `USER_CHECK`         | 로그인 로직 활성화 여부. FALSE이면 사용자가 executive sample user로 설정된다. |
| `ENROLLMENT_FEE`     | 동아리 가입비. |
| `CORS_ALL_ACCEPT`    | 개발용 설정. TRUE이면 모든 경로에 대해 허용한다.  |

## 실행 방법(with docker)

linux, docker가 요구됩니다. docker compose>=2.25.0가 요구됩니다.  

### Development 중

docker container를 빌드하고 실행합니다.
```bash
docker-compose up --build
```
vscode의 `Dev Containers` extensions에서 `open folder in container`을 통해 위에서 실행한 컨테이너로 연결합니다.

### Production 중

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## 실행 방법(without docker)

conda 환경을 설정 및 실행합니다. linux가 요구됩니다.

```bash
conda env create --file environment.yml
conda activate scsc_init_backend
```

db 파일을 생성합니다.
```bash
./script/init_db.sh YOUR_DB_FILENAME.db
```

(선택) 예시 데이터를 db에 추가합니다. 
```bash
./script/insert_majors.sh ./YOUR_DB_FILENAME.db ./docs/majors.csv
./script/insert_sample_users.sh ./YOUR_DB_FILENAME.db
```

(선택) 예시 데이터가 잘 추가되었는지 확인합니다. 
```bash
sqlite3 ./YOUR_DB_FILENAME.db "select * from major;"
sqlite3 ./YOUR_DB_FILENAME.db "select * from user;"
```

실행합니다. `fastapi-cli`를 요구합니다.
```bash
fastapi run main.py --host 0.0.0.0 --port 8080
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

## https 설정 및 실행

https 설정 후 main.py 25행의 `https_only=False` 값을 True로 바꿀 것이 요구됩니다.

Generate self-signed certs:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Run FastAPI dev server with HTTPS:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## 디렉토리 구조

| Path                | Description |
|---------------------|-------------|
| `/main.py`          | 애플리케이션 진입점 (entry point) |
| `/requirements.txt` | 필요한 Python 패키지 목록 (pip용) |
| `/environment.yml`  | Conda 환경 설정 파일 |
| `/.env`             | 환경 변수 설정 파일 |
| `/docs/`            | API 문서 등 프로젝트 관련 문서 |
| ├── `/common.md`    | 여러 라우터에서 사용되거나 중요한 로직 관련 문서 |
| ├── `/majors.csv`   | `2025학년도 대학 신입학생 입학전형 시행계획(첨단융합학부 반영).pdf` 문서 기준 서울대학교 학부 신입생 전공 자료 |
| `/script/`          | 프로젝트 관련 shell 명령어. `init_db.sh`은 DB 테이블 정의가 포함됨. |
| `/static/image/photo/` | 업로드된 이미지 보관 폴더 |
| `/download/`        | 업로드된 이미지 외 파일 보관 폴더 |
| `/src/`             | 메인 코드 디렉토리 (main.py 제외 전체 코드 포함) |
| ├── `/controller/`  | 여러 테이블을 조작하는 중요 로직 |
| ├── `/core/`        | 환경 변수 등 프로젝트 전역 설정 로직 |
| ├── `/db/`          | SQLite3 DB 연결 및 설정 관련 코드 |
| ├── `/middleware/`  | 미들웨어 정의 및 처리 |
| ├── `/model/`       | DB 테이블 정의 및 ORM 모델 |
| └── `/routes/`      | API 라우터 모음 |
| &nbsp;&nbsp;&nbsp;&nbsp;└── `__init__.py` | 루트 라우터 |
