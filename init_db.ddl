CREATE SCHEMA library;

SET search_path TO public, library;

CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS library.book (id uuid primary key default uuid_generate_v4(), title TEXT NOT NULL, description TEXT, volume INT NOT NULL, type TEXT, year INT, created timestamp with time zone default CURRENT_TIMESTAMP, modified timestamp with time zone default CURRENT_TIMESTAMP);

INSERT INTO library.book (title, type, year, volume) 
    SELECT 'some book name', 
    case when RANDOM() < 0.3 then 'magazine' else 'book' end,
    generate_series(0, 2023),
    floor(random()*(1000));

CREATE INDEX book_year_idx ON library.book(year);

CREATE TABLE IF NOT EXISTS library.author 
    (id uuid primary key default uuid_generate_v4(), 
    full_name TEXT NOT NULL, 
    created timestamp with time zone default CURRENT_TIMESTAMP, 
    modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS library.book_author 
    (id uuid primary key default uuid_generate_v4(), 
    book_id uuid references library.book,
    author_id uuid references library.author,
    created timestamp with time zone default CURRENT_TIMESTAMP);

CREATE UNIQUE INDEX book_author_idx ON library.book_author (book_id, author_id);

CREATE TABLE IF NOT EXISTS library.genre 
    (id uuid primary key default uuid_generate_v4(), 
    name text not null, 
    description text, 
    created timestamp with time zone default CURRENT_TIMESTAMP, 
    modified timestamp with time zone default CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS library.book_genre 
    (id uuid primary key default uuid_generate_v4(), 
    book_id uuid references library.book, 
    genre_id uuid references library.genre, 
    created timestamp with time zone default CURRENT_TIMESTAMP);

CREATE UNIQUE INDEX book_genre_idx ON library.book_genre (book_id, genre_id);
