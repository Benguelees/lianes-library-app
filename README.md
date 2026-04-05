# Liane's Library

A Streamlit app to manage books, friends, and borrowing activity.

## Features
- Add and manage books
- Add and manage friends
- Borrow and return books
- Track current loans
- View loan history
- Show top borrowers
- Delete books, friends, and loan records

## Tools Used
- Python
- Streamlit
- SQLite
- SQLAlchemy
- Pandas

## Project Goal
This project was built to practice connecting Python with SQL and creating a simple library management workflow with a small analytical feature.

## App Overview
![App Overview](screenshots/overview.png)

## Insights
The app includes an insights section that highlights the most active borrowers based on the total number of loans.

![Insights](screenshots/top_borrowers.png)

## Delete Functionality
The app also allows deleting books, friends, and loan records directly from the interface.

![Delete Functionality](screenshots/deleting.png)

## How to Run
```bash
pip install streamlit sqlalchemy pandas
streamlit run app.py