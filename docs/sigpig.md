# SIG/PIG 관련 DB, API 명세서
**최신개정일:** 2025-05-13

# DB 구조

## SIG/PIG DB
```sql
CREATE TABLE sig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_src TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'surveying' NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),
    UNIQUE (title, year, semester),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT
);
```

```sql
CREATE TABLE pig (
    ... -- same as sig
);
```

## SIG/PIG MEMBER DB
```sql
CREATE TABLE sig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES sig(id) ON DELETE CASCADE
);
```

```sql
CREATE TABLE pig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES pig(id) ON DELETE CASCADE
);
```

## SQL 관련
```sql
CREATE INDEX idx_sig_owner ON sig(owner);
CREATE INDEX idx_sig_term ON sig(year, semester);
CREATE INDEX idx_sig_member_user ON sig_member(user_id);
CREATE INDEX idx_sig_member_ig ON sig_member(ig_id);
CREATE INDEX idx_pig_member_user ON pig_member(user_id);
CREATE INDEX idx_pig_member_ig ON pig_member(ig_id);
```

```sql
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE ON sig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_src != NEW.content_src OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE sig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_pig_updated_at
AFTER UPDATE ON pig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_src != NEW.content_src OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE pig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
```

# API 구조

## SIG 관련 API(/api/sig)

- GET /api/sig/:id
- GET /api/sigs
- POST /api/sig/create
- POST /api/sig/update/:id
- POST /api/sig/delete/:id
- POST /api/executive/sig/update/:id
- POST /api/executive/sig/delete/:id

## SIG 구성원 관련 API (/api/sig-member)

- GET /api/sig-members/:sig_id
- POST /api/sig-member/join/:sig_id/me
- POST /api/sig-member/leave/:sig_id/me
- POST /api/executive/sig-member/join/:sig_id
- POST /api/executive/sig-member/leave/:sig_id

## PIG 관련 API(/api/pig)
`/api/sig`에서 `sig`를 `pig`로 바꾼다

## PIG 구성원 관련 API (/api/pig-members)
`/api/sig`에서 `sig`를 `pig`로 바꾼다
