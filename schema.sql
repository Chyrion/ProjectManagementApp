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
    permission INTEGER,
    creator BOOLEAN DEFAULT FALSE
);

CREATE TABLE ProjectTasks (
    id SERIAL PRIMARY KEY,
    pid INTEGER,
    name TEXT,
    description TEXT,
    deadline DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE TasksUsers (
    tid INTEGER REFERENCES ProjectTasks(id),
    uid INTEGER REFERENCES Users(id)
);