CREATE TABLE w_html_metadata (
    name TEXT PRIMARY KEY,
    size INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner TEXT,

    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE SET NULL
);

CREATE TRIGGER update_w_html_metadata_updated_at
AFTER UPDATE OF size, owner ON w_html_metadata 
FOR EACH ROW
BEGIN 
    UPDATE w_html_metadata SET updated_at = CURRENT_TIMESTAMP WHERE name = OLD.name; 
END;