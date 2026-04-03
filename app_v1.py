import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date

engine = create_engine("sqlite:///liane_library.db")

st.title("Liane's Library")
st.write("Track books, friends, and borrowed books.")

# --------------------------
# Show all books
# --------------------------
st.header("Books")

with engine.connect() as connection:
    books_result = connection.execute(text("SELECT * FROM books"))
    books_df = pd.DataFrame(books_result.fetchall(), columns=books_result.keys())

if not books_df.empty:
    st.write(books_df)
else:
    st.write("No books found.")

# --------------------------
# Show all friends
# --------------------------
st.header("Friends")

with engine.connect() as connection:
    friends_result = connection.execute(text("SELECT * FROM friends"))
    friends_df = pd.DataFrame(friends_result.fetchall(), columns=friends_result.keys())

if not friends_df.empty:
    st.write(friends_df)
else:
    st.write("No friends found.")

# --------------------------
# Borrow a book
# Only show books that are NOT currently borrowed
# --------------------------
st.header("Borrow a Book")

with engine.connect() as connection:
    available_books_result = connection.execute(text("""
        SELECT id, title
        FROM books
        WHERE id NOT IN (
            SELECT book_id
            FROM loans
            WHERE returned = 0
        )
    """))
    available_books = available_books_result.fetchall()

    friends_result = connection.execute(text("SELECT id, name FROM friends"))
    friends = friends_result.fetchall()

if available_books:
    book_options = {book[1]: book[0] for book in available_books}
    friend_options = {friend[1]: friend[0] for friend in friends}

    selected_book = st.selectbox("Select a book", list(book_options.keys()))
    selected_friend = st.selectbox("Select a friend", list(friend_options.keys()))
    borrow_date = st.date_input("Borrow date", value=date.today())

    if st.button("Save loan"):
        book_id = book_options[selected_book]

        with engine.connect() as connection:
            check = connection.execute(text("""
                SELECT *
                FROM loans
                WHERE book_id = :book_id AND returned = 0
            """), {"book_id": book_id}).fetchone()

            if check:
                st.error("This book is already borrowed!")
            else:
                connection.execute(text("""
                    INSERT INTO loans (book_id, friend_id, borrow_date, returned)
                    VALUES (:book_id, :friend_id, :borrow_date, 0)
                """), {
                    "book_id": book_id,
                    "friend_id": friend_options[selected_friend],
                    "borrow_date": str(borrow_date)
                })
                connection.commit()

                st.success("Loan saved.")
else:
    st.write("No books are currently available to borrow.")

# --------------------------
# Show current active loans only
# --------------------------
st.header("Current Loans")

with engine.connect() as connection:
    loans_result = connection.execute(text("""
        SELECT
            loans.id,
            books.title,
            friends.name,
            loans.borrow_date,
            loans.returned
        FROM loans
        JOIN books ON loans.book_id = books.id
        JOIN friends ON loans.friend_id = friends.id
        WHERE loans.returned = 0
        ORDER BY loans.id
    """))

    loans_df = pd.DataFrame(loans_result.fetchall(), columns=loans_result.keys())

if not loans_df.empty:
    st.write(loans_df)
else:
    st.write("No active loans found.")

# --------------------------
# Return a book
# --------------------------
st.header("Return a Book")

if not loans_df.empty:
    loan_options = {
        f"{row['title']} → {row['name']} ({row['borrow_date']})": row['id']
        for _, row in loans_df.iterrows()
    }

    selected_loan = st.selectbox("Select loan to return", list(loan_options.keys()))

    if st.button("Return book"):
        with engine.connect() as connection:
            connection.execute(text("""
                UPDATE loans
                SET returned = 1
                WHERE id = :loan_id
            """), {"loan_id": loan_options[selected_loan]})
            connection.commit()

        st.success("Book returned.")
else:
    st.write("No active loans to return.")