CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    password TEXT
);

CREATE TABLE Projects (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    deadline DATE NOT NULL DEFAULT CURRENT_DATE,
    status INTEGER
);

CREATE TABLE ProjectUsers (
    pid INTEGER,
    uid INTEGER,
    permission INTEGER
);

CREATE TABLE ProjectTasks (
    id SERIAL PRIMARY KEY,
    pid INTEGER,
    name TEXT,
    description TEXT,
    deadline DATE NOT NULL DEFAULT CURRENT_DATE
);