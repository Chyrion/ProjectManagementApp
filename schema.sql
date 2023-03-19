CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE Projects (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    deadline DATE NOT NULL
);

CREATE TABLE ProjectUsers (
    pid INTEGER REFERENCES Projects,
    uid INTEGER REFERENCES Users
);