BEGIN TRANSACTION;

CREATE TABLE attachment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    UNIQUE (article_id, file_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES file_metadata(id) ON DELETE CASCADE
);

COMMIT;
