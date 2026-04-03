from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///liane_library.db")

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT UNIQUE,
            author TEXT
        )
    """))

    connection.execute(text("""
        INSERT OR IGNORE INTO books (title, author)
        VALUES ('Harry Potter', 'J.K. Rowling')
    """))

    connection.commit()

    print("Table ready, duplicate-safe insert attempted.")

    result = connection.execute(text("SELECT * FROM books"))

    for row in result:
        print(row)