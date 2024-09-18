CREATE KEYSPACE IF NOT EXISTS sampledata WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};

USE sampledata;

CREATE TABLE IF NOT EXISTS books (
    book_id INT PRIMARY KEY,
    title TEXT
);

INSERT INTO books (book_id, title) VALUES (1, 'Cantebury tales');
INSERT INTO books (book_id, title) VALUES (2, 'Bible');
INSERT INTO books (book_id, title) VALUES (3, 'Dictionary');
INSERT INTO books (book_id, title) VALUES (4, 'Pride and Prjudice');
INSERT INTO books (book_id, title) VALUES (5, 'Winnie the Pooh');

CREATE TABLE IF NOT EXISTS book_status (
    book_status_id INT,
    title TEXT,
    status TEXT,  -- ENUM is not supported in Cassandra; use TEXT instead
    user TEXT,
    PRIMARY KEY (book_status_id)
);

INSERT INTO book_status (book_status_id, title, status, user) VALUES (1, 'Cantebury tales', 'free', 'free');
INSERT INTO book_status (book_status_id, title, status, user) VALUES (2, 'Bible', 'free', 'free');
INSERT INTO book_status (book_status_id, title, status, user) VALUES (3, 'Dictionary', 'free', 'free');
INSERT INTO book_status (book_status_id, title, status, user) VALUES (4, 'Pride and Prjudice', 'free', 'free');
INSERT INTO book_status (book_status_id, title, status, user) VALUES (5, 'Winnie the Pooh', 'free', 'free');
