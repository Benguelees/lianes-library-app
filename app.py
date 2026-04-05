import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date

engine = create_engine("sqlite:///liane_library.db")

st.set_page_config(page_title="Liane's Library", layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.6rem !important;
        }
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
st.title("Liane's Library")
st.caption("Track books, friends, and borrowed books.")

# --------------------------
# Add Book / Add Friend
# --------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Add a Book")
    new_title = st.text_input("Book title")
    new_author = st.text_input("Author")

    if st.button("Add book"):
        if new_title.strip() == "" or new_author.strip() == "":
            st.error("Please enter both title and author.")
        else:
            with engine.connect() as connection:
                existing_book = connection.execute(
                    text("""
                        SELECT *
                        FROM books
                        WHERE title = :title
                    """),
                    {"title": new_title.strip()}
                ).fetchone()

                if existing_book:
                    st.error("This book already exists.")
                else:
                    connection.execute(
                        text("""
                            INSERT INTO books (title, author)
                            VALUES (:title, :author)
                        """),
                        {
                            "title": new_title.strip(),
                            "author": new_author.strip()
                        }
                    )
                    connection.commit()
                    st.success("Book added. Refresh the page if you do not see it immediately.")

with col2:
    st.subheader("Add a Friend")
    new_friend = st.text_input("Friend name")

    if st.button("Add friend"):
        if new_friend.strip() == "":
            st.error("Please enter a friend name.")
        else:
            with engine.connect() as connection:
                existing_friend = connection.execute(
                    text("""
                        SELECT *
                        FROM friends
                        WHERE name = :name
                    """),
                    {"name": new_friend.strip()}
                ).fetchone()

                if existing_friend:
                    st.error("This friend already exists.")
                else:
                    connection.execute(
                        text("""
                            INSERT INTO friends (name)
                            VALUES (:name)
                        """),
                        {"name": new_friend.strip()}
                    )
                    connection.commit()
                    st.success("Friend added. Refresh the page if you do not see it immediately.")

st.write("---")

# --------------------------
# Books / Friends
# --------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Books")
    with engine.connect() as connection:
        books_result = connection.execute(text("""
            SELECT id, title, author
            FROM books
            ORDER BY title
        """))
        books_df = pd.DataFrame(books_result.fetchall(), columns=books_result.keys())

    if not books_df.empty:
        st.markdown(books_df[["title", "author"]].to_html(index=False), unsafe_allow_html=True)
    else:
        st.write("No books found.")

with col4:
    st.subheader("Friends")
    with engine.connect() as connection:
        friends_result = connection.execute(text("""
            SELECT id, name
            FROM friends
            ORDER BY name
        """))
        friends_df = pd.DataFrame(friends_result.fetchall(), columns=friends_result.keys())

    if not friends_df.empty:
        st.markdown(friends_df[["name"]].to_html(index=False), unsafe_allow_html=True)
    else:
        st.write("No friends found.")

st.write("---")

# --------------------------
# Borrow a Book
# --------------------------
st.subheader("Borrow a Book")

with engine.connect() as connection:
    available_books_result = connection.execute(text("""
        SELECT id, title
        FROM books
        WHERE id NOT IN (
            SELECT book_id
            FROM loans
            WHERE returned = 0
        )
        ORDER BY title
    """))
    available_books = available_books_result.fetchall()

    friends_result = connection.execute(text("""
        SELECT id, name
        FROM friends
        ORDER BY name
    """))
    friends = friends_result.fetchall()

if available_books and friends:
    borrow_col1, borrow_col2, borrow_col3 = st.columns(3)

    book_options = {book[1]: book[0] for book in available_books}
    friend_options = {friend[1]: friend[0] for friend in friends}

    with borrow_col1:
        selected_book = st.selectbox("Select a book", list(book_options.keys()))

    with borrow_col2:
        selected_friend = st.selectbox("Select a friend", list(friend_options.keys()))

    with borrow_col3:
        borrow_date = st.date_input("Borrow date", value=date.today())

    if st.button("Save loan"):
        book_id = book_options[selected_book]
        friend_id = friend_options[selected_friend]
        borrow_date_str = str(borrow_date)

        with engine.connect() as connection:
            check = connection.execute(text("""
                SELECT *
                FROM loans
                WHERE book_id = :book_id
                  AND friend_id = :friend_id
                  AND borrow_date = :borrow_date
                  AND returned = 0
            """), {
                "book_id": book_id,
                "friend_id": friend_id,
                "borrow_date": borrow_date_str
            }).fetchone()

            already_borrowed = connection.execute(text("""
                SELECT *
                FROM loans
                WHERE book_id = :book_id
                  AND returned = 0
            """), {
                "book_id": book_id
            }).fetchone()

            if check:
                st.error("This exact loan already exists!")
            elif already_borrowed:
                st.error("This book is already borrowed!")
            else:
                connection.execute(
    text("""
        INSERT INTO loans (book_id, friend_id, borrow_date, returned)
        VALUES (:book_id, :friend_id, :borrow_date, 0)
    """),
    {
        "book_id": book_id,
        "friend_id": friend_id,
        "borrow_date": borrow_date_str
    }
)
                connection.commit()
                st.success("Loan saved. Refresh the page if you do not see it immediately.")
else:
    if not available_books:
        st.write("No books are currently available to borrow.")
    if not friends:
        st.write("No friends available. Add a friend first.")

st.write("---")

# --------------------------
# Current Loans / Return a Book
# --------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Current Loans")

    with engine.connect() as connection:
        loans_result = connection.execute(text("""
            SELECT
                 books.title AS book,
                friends.name AS friend,
                loans.borrow_date AS borrow_date
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN friends ON loans.friend_id = friends.id
            WHERE loans.returned = 0
            ORDER BY loans.borrow_date, books.title
        """))

        loans_df = pd.DataFrame(loans_result.fetchall(), columns=loans_result.keys())

    if not loans_df.empty:
        st.markdown(loans_df.to_html(index=False), unsafe_allow_html=True)
    else:
        st.write("No active loans found.")

with right_col:
    st.subheader("Return a Book")

    with engine.connect() as connection:
        return_result = connection.execute(text("""
            SELECT
                loans.id,
                books.title,
                friends.name,
                loans.borrow_date
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN friends ON loans.friend_id = friends.id
            WHERE loans.returned = 0
            ORDER BY loans.id
        """))
        active_loans = return_result.fetchall()

    if active_loans:
        loan_options = {
            f"{row.title} → {row.name} ({row.borrow_date})": row.id
            for row in active_loans
        }

        selected_loan = st.selectbox(
            "Select loan to return",
            list(loan_options.keys()),
            key="return_loan_select"
        )

        if st.button("Return book"):
            with engine.connect() as connection:
                connection.execute(text("""
                    UPDATE loans
                    SET returned = 1
                    WHERE id = :loan_id
                """), {"loan_id": loan_options[selected_loan]})
                connection.commit()

            st.success("Book returned. Refresh the page if you do not see it immediately.")
    else:
        st.write("No active loans to return.")

st.write("---")

# --------------------------
# Top Borrowers
# --------------------------
st.subheader("Insights")
st.caption("Top borrowers based on number of loans.")

with engine.connect() as connection:
    top_borrowers_result = connection.execute(text("""
        SELECT
            friends.name,
            COUNT(*) AS total_loans
        FROM loans
        JOIN friends ON loans.friend_id = friends.id
        GROUP BY friends.name
        ORDER BY total_loans DESC, friends.name
    """))

    top_borrowers_df = pd.DataFrame(
        top_borrowers_result.fetchall(),
        columns=top_borrowers_result.keys()
    )

if not top_borrowers_df.empty:
    st.markdown(top_borrowers_df.to_html(index=False), unsafe_allow_html=True)
else:
    st.write("No borrowing data yet.")

st.write("---")



# --------------------------
# Loan History
# --------------------------
st.subheader("Loan History")

with engine.connect() as connection:
    history_result = connection.execute(text("""
        SELECT
            books.title AS book,
            friends.name AS friend,
            loans.borrow_date AS borrow_date,
            CASE
                WHEN loans.returned = 1 THEN 'Returned'
                ELSE 'Borrowed'
            END AS status
        FROM loans
        JOIN books ON loans.book_id = books.id
        JOIN friends ON loans.friend_id = friends.id
        ORDER BY loans.borrow_date DESC, books.title
    """))

    history_df = pd.DataFrame(history_result.fetchall(), columns=history_result.keys())

if not history_df.empty:
    st.markdown(history_df.to_html(index=False), unsafe_allow_html=True)
else:
    st.write("No history yet.")

st.write("---")



# --------------------------
# Delete Records
# --------------------------
st.subheader("Delete Records")

delete_col1, delete_col2, delete_col3 = st.columns(3)

# --------------------------
# Delete a Book
# --------------------------
with delete_col1:
    st.markdown("### Delete a Book")

    with engine.connect() as connection:
        delete_books_result = connection.execute(text("""
            SELECT id, title, author
            FROM books
            ORDER BY title
        """))
        delete_books = delete_books_result.fetchall()

    if delete_books:
        delete_book_options = {
            f"{row.title} by {row.author}": row.id
            for row in delete_books
        }

        selected_book_to_delete = st.selectbox(
            "Select book to delete",
            list(delete_book_options.keys()),
            key="delete_book_select"
        )

        also_delete_book_history = st.checkbox(
            "Also delete all loan history for this book",
            key="delete_book_history_checkbox"
        )

        if st.button("Delete selected book", key="delete_book_button"):
            book_id = delete_book_options[selected_book_to_delete]

            with engine.connect() as connection:
                loan_exists = connection.execute(text("""
                    SELECT 1
                    FROM loans
                    WHERE book_id = :book_id
                    LIMIT 1
                """), {"book_id": book_id}).fetchone()

                if loan_exists:
                    if also_delete_book_history:
                        connection.execute(text("""
                            DELETE FROM loans
                            WHERE book_id = :book_id
                        """), {"book_id": book_id})

                        connection.execute(text("""
                            DELETE FROM books
                            WHERE id = :book_id
                        """), {"book_id": book_id})

                        connection.commit()
                        st.success("Book and all related loan history deleted. Refresh the page if needed.")
                    else:
                        st.error("This book has loan history. Tick the box if you want to delete the book and its history.")
                else:
                    connection.execute(text("""
                        DELETE FROM books
                        WHERE id = :book_id
                    """), {"book_id": book_id})
                    connection.commit()
                    st.success("Book deleted. Refresh the page if needed.")
    else:
        st.write("No books available to delete.")

# --------------------------
# Delete a Friend
# --------------------------
with delete_col2:
    st.markdown("### Delete a Friend")

    with engine.connect() as connection:
        delete_friends_result = connection.execute(text("""
            SELECT id, name
            FROM friends
            ORDER BY name
        """))
        delete_friends = delete_friends_result.fetchall()

    if delete_friends:
        delete_friend_options = {
            row.name: row.id
            for row in delete_friends
        }

        selected_friend_to_delete = st.selectbox(
            "Select friend to delete",
            list(delete_friend_options.keys()),
            key="delete_friend_select"
        )

        also_delete_friend_history = st.checkbox(
            "Also delete all loan history for this friend",
            key="delete_friend_history_checkbox"
        )

        if st.button("Delete selected friend", key="delete_friend_button"):
            friend_id = delete_friend_options[selected_friend_to_delete]

            with engine.connect() as connection:
                loan_exists = connection.execute(text("""
                    SELECT 1
                    FROM loans
                    WHERE friend_id = :friend_id
                    LIMIT 1
                """), {"friend_id": friend_id}).fetchone()

                if loan_exists:
                    if also_delete_friend_history:
                        connection.execute(text("""
                            DELETE FROM loans
                            WHERE friend_id = :friend_id
                        """), {"friend_id": friend_id})

                        connection.execute(text("""
                            DELETE FROM friends
                            WHERE id = :friend_id
                        """), {"friend_id": friend_id})

                        connection.commit()
                        st.success("Friend and all related loan history deleted. Refresh the page if needed.")
                    else:
                        st.error("This friend has loan history. Tick the box if you want to delete the friend and their history.")
                else:
                    connection.execute(text("""
                        DELETE FROM friends
                        WHERE id = :friend_id
                    """), {"friend_id": friend_id})
                    connection.commit()
                    st.success("Friend deleted. Refresh the page if needed.")
    else:
        st.write("No friends available to delete.")

# --------------------------
# Delete a Loan Record
# --------------------------
with delete_col3:
    st.markdown("### Delete a Loan Record")

    with engine.connect() as connection:
        delete_loans_result = connection.execute(text("""
            SELECT
                loans.id,
                books.title,
                friends.name,
                loans.borrow_date,
                loans.returned
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN friends ON loans.friend_id = friends.id
            ORDER BY loans.borrow_date DESC, loans.id DESC
        """))
        delete_loans = delete_loans_result.fetchall()

    if delete_loans:
        delete_loan_options = {
            f"{row.title} → {row.name} ({row.borrow_date}) - {'Returned' if row.returned == 1 else 'Borrowed'}": row.id
            for row in delete_loans
        }

        selected_loan_to_delete = st.selectbox(
            "Select loan record to delete",
            list(delete_loan_options.keys()),
            key="delete_loan_select"
        )

        if st.button("Delete selected loan record", key="delete_loan_button"):
            loan_id = delete_loan_options[selected_loan_to_delete]

            with engine.connect() as connection:
                connection.execute(text("""
                    DELETE FROM loans
                    WHERE id = :loan_id
                """), {"loan_id": loan_id})
                connection.commit()

            st.success("Loan record deleted. Refresh the page if needed.")
    else:
        st.write("No loan records available to delete.")