# homepage_init_backend

SCSC 홈페이지 Main BE 문서

> 최초작성일: 2025-04-30  
> 최신개정일: 2025-10-05  
> 최신개정자: [윤영우](dan.yun0821@gmail.com)  
> 작성자: [강명석](tomskang@naver.com), 이한경, [윤영우](dan.yun0821@gmail.com)  

## 브랜치

- main: 배포된 코드를 저장하며 버전 별로 태그가 붙어 있습니다.
- develop(default): 개발 중인 코드를 저장합니다.

## .env 파일

.env 파일은 반드시 root에 위치해야 하며 아래 형식으로 작성합니다. 아래 예시 env에 없는 항목은 하드코딩된 기본 값이 설정되어 있습니다. `src.core.config.py`에서 확인할 수 있습니다. env 파일에서 이를 설정하면 기본 값보다 env 파일 값이 우선하여 적용됩니다.

```env
API_SECRET="some-secret-code"
JWT_SECRET="some-session-secret"
JWT_VALID_SECONDS=3600
SQLITE_FILENAME="db/YOUR_DB_FILENAME.db"
NOTICE_CHANNEL_ID=0
GRANT_CHANNEL_ID=0
```

| Key Name             | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `API_SECRET`             | API 요청 시 검증에 사용되는 비밀 코드. 일치하지 않으면 401 반환  |
| `JWT_SECRET`             | 로그인 관련 JWT를 암호화하거나 검증하는 데 사용하는 비밀 키          |
| `JWT_VALID_SECONDS`      | 로그인 관련 JWT 유효 시간(초)          |
| `SQLITE_FILENAME`        | SQLite3 데이터베이스 파일의 경로 또는 파일 이름                  |
| `IMAGE_DIR`              | 이미지 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `FILE_DIR`               | 파일 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `FILE_MAX_SIZE`          | 파일 최대 용량(바이트) |
| `ARTICLE_DIR`            | 글 업로드 경로. 폴더가 이미 생성되어 있어야 함 |
| `USER_CHECK`             | 로그인 로직 활성화 여부. FALSE이면 사용자가 executive sample user로 설정된다. |
| `ENROLLMENT_FEE`         | 동아리 가입비. |
| `CORS_ALL_ACCEPT`        | 개발용 설정. TRUE이면 모든 경로에 대해 허용한다.  |
| `RABBITMQ_HOST`          | RabbitMQ가 돌아가는 호스트명. docker의 경우 container 이름과 동일. |
| `BOT_HOST`               | 디스코드 봇이 돌아가는 호스트명. docker의 경우 container 이름과 동일. |
| `DISCORD_RECEIVE_QUEUE`  | 메인 서버에서 요청을 받는 큐의 명칭. 봇 서버의 환경 변수명과 동일해야 함. |
| `RABBITMQ_REQUIRED`      | RabbitMQ 서버와의 연결 여부. FALSE이면 연결을 시도하지 않고, TRUE이면 연결 시도 후 실패 시 오류를 띄움. |
| `NOTICE_CHANNEL_ID`      | 디스코드 서버에서 공지 채널의 ID. |
| `GRANT_CHANNEL_ID`       | 디스코드 서버에서 지원금 신청 채널의 ID. |
| `W_HTML_DIR`             | HTML 파일 업로드 경로. 폴더가 이미 생성되어 있어야 함 |

## 기타 설정 파일

### `script/migrations/president.csv`(Optional)

- DB 초기화 시 자동으로 사용자 테이블에 추가되는 president 권한을 가진 사용자 목록을 정의합니다
- `script/insert_sample_data/president.example.csv`의 형식을 참고하여 작성합니다
- 예시 파일에 포함된 값은 마이그래이션 파일에 의해 이미 추가된 값으로 `presidents.csv` 파일에 포함할 필요가 없습니다. 포함하면 오류 없이 무시됩니다. 


## 실행 방법(with docker)

linux, docker가 요구됩니다. docker compose>=2.25.0가 요구됩니다.  

docker container를 빌드하고 실행합니다.
```bash
docker-compose up --build
```


## 실행 방법(without docker)

루트에 다음 명령어로 필요한 폴더를 추가합니다.

```bash
mkdir -p \
  ./db \
  ./logs \
  ./static/download \
  ./static/article \
  ./static/image/photo \
  ./static/image/pfps
```

db 파일을 생성합니다.
```bash
./script/migrations/index.sh ./db/YOUR_DB_FILENAME.db
```

(선택) 예시 데이터를 db에 추가합니다. 
```bash
./script/insert_sample_data/index.sh ./db/YOUR_DB_FILENAME.db
```

(선택) 예시 데이터가 잘 추가되었는지 확인합니다. 
```bash
sqlite3 ./YOUR_DB_FILENAME.db "select * from major;"
sqlite3 ./YOUR_DB_FILENAME.db "select * from user;"
```

실행합니다. `uv`를 요구합니다. `uv` 설정에 관련된 내용은 하단의 `developer tips` 절에 설명됩니다.  
```bash
uv run python main.py --host 0.0.0.0 --port 8080
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

## developer tips

### 개발 환경 설정

package manager로 uv를 사용합니다.  

uv로 파이썬 가상환경을 만듭니다. 가상환경을 실행 후 `uv.lock`에서 명시된 dependency를 모두 설치합니다.  

```bash
uv venv
source .venv/bin/activate
uv sync --locked
```

다음으로 pre-commit을 uv로 설정합니다.

```bash
uv run pre-commit install
```

### dependency 변경

dependency 변경이 필요한 경우, uv를 사용하고, `pyproject.toml`과 `uv.lock`을 변경합니다. 다음은 패키지를 추가하는 예시입니다.  

```bash
uv add fastapi
uv add --dev pytest black
uv lock
uv sync --locked
```

이에 맞춰 `requirements.txt`도 반드시 같이 업데이트합니다.
```bash
uv pip compile pyproject.toml -o requirements.txt --no-deps
```

### DB clear

DB 및 연관된 데이터 파일을 모두 삭제합니다.(실행 후 DB 파일을 다시 생성할 필요가 있습니다. 단, docker compose 실행 시에는 DB 파일을 체크하고 없을 시 자동으로 entry에서 생성하므로, 수동으로 파일을 생성할 필요는 없습니다.)  

`./script/clear_db.sh`를 실행합니다.


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
## Tests
Pytest는 파이썬 테스트 러너로, 이 프로젝트의 모든 API/서비스 시나리오를 자동으로 검증합니다. 다음 명령어를 통해 pytest를 실행시킵니다.

```bash
uv run env PYTHONPATH=. pytest
```

## 디렉토리 구조

| Path                | Description |
|---------------------|-------------|
| `/main.py`          | 애플리케이션 진입점 (entry point) |
| `/requirements.txt` | 필요한 Python 패키지 목록 (pip용) |
| `/environment.yml`  | Conda 환경 설정 파일 |
| `/.env`             | 환경 변수 설정 파일 |
| `/logs/`            | 로그 파일이 저장되는 폴더 |
| `/docs/`            | API 문서 등 프로젝트 관련 문서 |
| ├── `common.md`     | 여러 라우터에서 사용되거나 중요한 로직 관련 문서 |
| ├── `majors.csv`    | `2025학년도 대학 신입학생 입학전형 시행계획(첨단융합학부 반영).pdf` 문서 기준 서울대학교 학부 신입생 전공 자료 |
| `/script/`          | 프로젝트 관련 명령어 |
| ├── `migrations/`   | sql 관련 명령어 |
| `/static/`          | 업로드된 파일 보관 폴더 |
| ├── `image/photo/`  | 업로드된 이미지 보관 폴더 |
| ├── `image/pfps/`   | 업로드된 프로필 이미지 보관 폴더 |
| ├── `download/`     | 업로드된 이미지 외 파일 보관 폴더 |
| `/src/`             | 메인 코드 디렉토리 (main.py 제외 전체 코드 포함) |
| ├── `controller/`   | 여러 테이블을 조작하는 중요 로직 |
| ├── `core/`         | 환경 변수 등 프로젝트 전역 설정 로직 |
| ├── `db/`           | SQLite3 DB 연결 및 설정 관련 코드 |
| ├── `middleware/`   | 미들웨어 정의 및 처리 |
| ├── `model/`        | DB 테이블 정의 및 ORM 모델 |
| ├── `routes/`       | API 라우터 모음 |
| ├──├── `__init__.py` | 루트 라우터 |

## Migration details for devs

### Migration: conda + pip -> uv

package manager을 **conda + pip** 을 **[uv](https://github.com/astral-sh/uv)** 로 변경합니다.([via Pull#121](https://github.com/scsc-init/homepage_init_backend/pull/121))

**배경**  

- 속도가 빠름
- homepage_init_backend venv는 이 레포지토리 단 하나에서만 쓰일 것이므로 uv로 관리하여도 충분함
- pyproject.toml을 쓰기 용이하다

**설명**

1. conda 환경 제거

```bash
conda deactivate
conda env remove -n homepage_init_backend # or whatever your env name is
```

2. uv 설치 및 설정

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh # might need to restart shell after installation
uv venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows
uv lock
uv sync --locked
```

**기타**

- As of now, **live edits inside the docker container do not work** as the code files are not mounted. Therefore, to apply updates to the code into the container image, devs must rebuild the container.

- In `./Dockerfile`, we setup a nonroot user to execute the application and modify static files. At production, we encourage the devs to add gid and uid that is appropriate for the host server, so that they have access to static files at host machine.

### Migration: Add black, isort, pre-commit

[`black`](https://github.com/psf/black), [`isort`](https://github.com/PyCQA/isort), [`pre-commit`](https://github.com/pre-commit/pre-commit)을 도입합니다.  

**배경**  

- 좋은 포맷
- 코드의 통일성
- 버그, 충돌 방지

**설명**

1. deps 변경 (dev deps 추가)

```bash
uv lock
uv sync --locked
```

2. pre-commit 설치

```bash
uv run pre-commit install
```

3. (선택) pre-commit 테스트

**주의**: 이 명령은 설정된 모든 파일을 변경합니다.

```bash
uv run pre-commit run --all-files
```
