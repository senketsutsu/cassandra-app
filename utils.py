import time

def get_all_books(session):
    query = f"SELECT * FROM sampledata.books ;"
    return list(session.execute(query))

def avaiable_books(session):
    query = f"SELECT title FROM book_status WHERE status = 'free';"
    return set(session.execute(query))

def add_reservation(username, session, book_id):
    if book_id not in avaiable_books(session):
        raise Exception("The book is not available.")
    # Remove the book from available
    query = f"UPDATE sampledata.book_status SET status = 'reserved', user = '{username}'  WHERE title = '{book_id}';"
    session.execute(query)

def get_all_reservations(username, session):
    query = f"SELECT * FROM sampledata.book_status WHERE user = '{username}';"
    return list(session.execute(query))

def update_reservation(username, session, res_book, new_book): 
    # Add new book to taken
    query = f"UPDATE book_status SET status = 'reserved', user = '{username}' WHERE title = '{new_book}';"
    session.execute(query)
    # Update reservation
    query = f"UPDATE book_status SET status = 'free', user = 'free' WHERE title = '{res_book}', user = '{username}';"
    session.execute(query)

def delete_reservation(username, session, res_book):
    # Free the book
    query = f"UPDATE book_status SET status = 'free', user = 'free' WHERE title = '{res_book}', user = '{username}';"
    session.execute(query)