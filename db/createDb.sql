CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY,
    user_name TEXT,
    paswd TEXT,
    last_transaction TEXT DEFAULT 'none',
    logged_in INTEGER DEFAULT 0
);

CREATE TABLE messages (
    id INTEGER NOT NULL PRIMARY KEY,
    sender TEXT,
    receiver TEXT,
    creation_date TEXT,
    sbjct TEXT ,
    msg TEXT,
);

INSERT INTO users (id, user_name, paswd) values (1,'nate',  'natex');
INSERT INTO users (id, user_name, paswd) values (2,'yuri',  'yurix');
INSERT INTO users (id, user_name, paswd) values (3,'robin', 'robin');