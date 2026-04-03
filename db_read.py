from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///liane_library.db")

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM books"))

    for row in result:
        print(row)