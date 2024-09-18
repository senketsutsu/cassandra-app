from flask import Flask, request, render_template, redirect, url_for, session, flash
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.auth import PlainTextAuthProvider
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

def get_all_books(cassandra_session):
    query = "SELECT * FROM sampledata.book_status;"
    return list(cassandra_session.execute(query))

def available_books(cassandra_session):
    query = "SELECT title FROM sampledata.book_status WHERE status = 'free' ALLOW FILTERING;"
    return [row.title for row in cassandra_session.execute(query)]

def available_books_id(cassandra_session):
    query = "SELECT book_status_id FROM sampledata.book_status WHERE status = 'free' ALLOW FILTERING;"
    return [str(row.book_status_id) for row in cassandra_session.execute(query)]

def add_reservation(username, cassandra_session, book_id):
    if str(book_id) not in available_books_id(cassandra_session):
        raise Exception("The book is not available.")
    query = "UPDATE sampledata.book_status SET status = 'reserved', user = %s WHERE book_status_id = %s;"
    cassandra_session.execute(query, (username, int(book_id)))

def get_all_reservations_id(username, cassandra_session):
    query = "SELECT book_status_id FROM sampledata.book_status WHERE user = %s ALLOW FILTERING;"
    return [str(row.book_status_id) for row in cassandra_session.execute(query, (username,))]

def get_all_reservations(username, cassandra_session):
    query = "SELECT * FROM sampledata.book_status WHERE user = %s ALLOW FILTERING;"
    return list(cassandra_session.execute(query, (username,)))

def update_reservation(username, cassandra_session, res_book, new_book):
    if str(new_book) not in available_books_id(cassandra_session):
        raise Exception("The new book is not available.")
    query1 = "UPDATE sampledata.book_status SET status = 'reserved', user = %s WHERE book_status_id = %s;"
    query2 = "UPDATE sampledata.book_status SET status = 'free', user = 'free' WHERE book_status_id = %s;"
    cassandra_session.execute(query1, (username, int(new_book)))
    cassandra_session.execute(query2, (int(res_book),))

def delete_reservation(username, cassandra_session, res_book):
    if str(res_book) not in get_all_reservations_id(username, cassandra_session):
        raise Exception("The book is not available.")
    query = "UPDATE sampledata.book_status SET status = 'free', user = 'free' WHERE book_status_id = %s;"
    cassandra_session.execute(query, (int(res_book),))

def wait_for_cassandra():
    cluster = Cluster(contact_points=['cassandra-node1', 'cassandra-node2', 'cassandra-node3'], port=9042)
    while True:
        try:
            cluster.connect()  
            print("Connected to Cassandra.")
            break
        except NoHostAvailable:
            print("Cassandra is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)


def get_cassandra_session():
    cluster = Cluster(contact_points=['cassandra-node1', 'cassandra-node2', 'cassandra-node3'], port=9042)
    wait_for_cassandra()
    session = cluster.connect() 
    return session

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/set_username', methods=['POST'])
def set_username():
    username = request.form.get('username')  
    if username:
        session['username'] = username  
        flash('Username set successfully!', 'success')
        return redirect(url_for('operation'))  
    flash('Username is required', 'error')
    return redirect(url_for('index')) 

@app.route('/operation', methods=['GET'])
def operation():
    username = session.get('username')  
    if username:
        return render_template('operation.html', username=username)
    else:
        flash('Please set a username first.', 'error')
        return redirect(url_for('index'))


@app.route('/perform_operation', methods=['POST'])
def perform_operation():
    operation = request.form.get('operation')
    print(f"Received operation: {operation}")  
    if operation in ['list_books', 'show_available_books', 'reserve_book', 'user_reservations', 'update_reservation_route', 'delete_reservation_route']:
        return redirect(url_for(operation))
    else:
        flash('Invalid operation selected.', 'error')
        return redirect(url_for('operation'))

@app.route('/list_books', methods=['GET'])
def list_books():

    cassandra_session = get_cassandra_session()
    books = get_all_books(cassandra_session)
    return render_template('result.html', data=books, title="List of Books")


@app.route('/available_books', methods=['GET'])
def show_available_books():

    cassandra_session = get_cassandra_session()
    # available = available_books(cassandra_session)
    available = available_books_id(cassandra_session)
    return render_template('result.html', data=available, title="Available Books")


@app.route('/reserve_book', methods=['GET', 'POST'])
def reserve_book():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        username = session.get('username') 
        if username and book_id:
            cassandra_session = get_cassandra_session()
            add_reservation(username, cassandra_session, book_id)
            flash("Book reserved successfully!", 'success')
            return redirect(url_for('operation'))
        
        else:
            flash('Book ID is required.', 'error')
            return redirect(url_for('reserve_book'))
    else:
        username = session.get('username')
        return render_template('reserve_book.html', username=username)

@app.route('/user_reservations', methods=['GET'])
def user_reservations():
    cassandra_session = get_cassandra_session()
    username = session.get('username')  
    if username:
        reservations = get_all_reservations(username, cassandra_session)
        return render_template('result.html', data=reservations, title="Your Reservations")
    else:
        flash('Username is required.', 'error')
        return redirect(url_for('index'))


@app.route('/update_reservation', methods=['GET', 'POST'])
def update_reservation_route():
    if request.method == 'POST':
        res_book = request.form.get('res_book')
        new_book = request.form.get('new_book')
        username = session.get('username')  
        if username and res_book and new_book:
            cassandra_session = get_cassandra_session()
            update_reservation(username, cassandra_session, res_book, new_book)
            flash("Reservation updated successfully!", 'success')
            return redirect(url_for('operation'))
        
        else:
            flash('All fields are required.', 'error')
            return redirect(url_for('update_reservation_route'))
    else:
        username = session.get('username')
        return render_template('update_reservation.html', username=username)

@app.route('/delete_reservation', methods=['GET', 'POST'])
def delete_reservation_route():
    if request.method == 'POST':
        res_book = request.form.get('res_book')
        username = session.get('username')  
        if username and res_book:
            cassandra_session = get_cassandra_session()
        
            delete_reservation(username, cassandra_session, res_book)
            flash("Reservation deleted successfully!", 'success')
            return redirect(url_for('operation'))
        
        else:
            flash('Book title is required.', 'error')
            return redirect(url_for('delete_reservation_route'))
    else:
        username = session.get('username')
        return render_template('delete_reservation.html', username=username)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
