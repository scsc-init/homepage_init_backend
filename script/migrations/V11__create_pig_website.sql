CREATE TABLE pig_website (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pig_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (pig_id) REFERENCES pig(id) ON DELETE CASCADE
);

CREATE INDEX idx_pig_website_sort ON pig_website(pig_id, sort_order);

CREATE TRIGGER update_pig_website_updated_at
AFTER UPDATE OF label, url, sort_order ON pig_website
BEGIN
    UPDATE pig_website SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
