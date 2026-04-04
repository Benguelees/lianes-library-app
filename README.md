# Liane's Library App

This project is a small library management system designed to simulate real-world data handling scenarios such as tracking relationships between entities (books, users, and loans), preventing duplicate transactions, and maintaining data integrity.

---

## 🚀 Project Overview

The application allows users to manage a collection of books and track borrowing activity between friends. It focuses on handling relational data and ensuring consistency across operations such as adding, borrowing, and deleting records.

---

## 🧠 Key Features

- Add and manage books and friends
- Borrow and return books using a structured loan system
- Prevent duplicate borrowing of the same book
- Track borrowing activity and relationships between entities
- Delete records with optional cleanup of related data
- Maintain data integrity across all operations

---

## 🗄️ Data Model

The application is built around three main entities:

- **Books** → stores book titles and authors  
- **Friends** → stores user names  
- **Loans** → links books and friends (who borrowed what and when)

This structure simulates a relational database system where:
- one book can be borrowed multiple times
- one user can borrow multiple books
- relationships are tracked through a dedicated table

---

## ⚙️ Tech Stack

- Python  
- Streamlit  
- SQLite  
- SQLAlchemy  

---

## ▶️ How to Run

```bash
git clone https://github.com/YOUR_USERNAME/lianes-library-app.git
cd lianes-library-app
pip install streamlit sqlalchemy pandas
python db_setup.py
streamlit run app.py
