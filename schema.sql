CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    makeandmodel TEXT,
    type TEXT,
    location TEXT,
    availability TEXT,
    price INTEGER,
    description TEXT,
    user_id INTEGER REFERENCES users
);