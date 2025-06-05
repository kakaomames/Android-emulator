CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT UNIQUE,
    version_code INTEGER,
    version_name TEXT,
    label TEXT,
    icon_path TEXT,
    apk_path TEXT
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    name TEXT,
    exported INTEGER,
    intent_filters TEXT
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    name TEXT
);

CREATE TABLE IF NOT EXISTS signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    cert_sha256 TEXT
);
