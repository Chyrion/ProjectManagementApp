CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name TEXT
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
    uid INTEGER
);