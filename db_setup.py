from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///liane_library.db")

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT UNIQUE NOT NULL,
            author TEXT NOT NULL
        )
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            return_date TEXT,
            returned INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (friend_id) REFERENCES friends(id)
        )
    """))

    connection.execute(text("""
        INSERT OR IGNORE INTO books (title, author)
        VALUES
            ('Harry Potter', 'J.K. Rowling'),
            ('The Hobbit', 'J.R.R. Tolkien'),
            ('Pride and Prejudice', 'Jane Austen')
    """))

    connection.execute(text("""
        INSERT OR IGNORE INTO friends (name)
        VALUES
            ('Anna'),
            ('Ben'),
            ('Clara')
    """))

    connection.commit()

print("Database setup complete.")