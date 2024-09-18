import unittest
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.auth import PlainTextAuthProvider
import random
import time
import sys
import os

# Functions copied from the app.py 

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
    cluster = Cluster(contact_points=['127.0.0.1'], port=9042)
    while True:
        try:
            cluster.connect()  
            print("Connected to Cassandra.")
            break
        except NoHostAvailable:
            print("Cassandra is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)


def get_cassandra_session():
    cluster = Cluster(contact_points=['127.0.0.1'], port=9042)
    wait_for_cassandra()
    session = cluster.connect() 
    return session

# Stress Test 1: The client makes the same request very quickly min (10000 times).
# Stress Test 2: Two or more clients make the possible requests randomly (10000 times).
# Stress Test 3: Immediate occupancy of all seats/reservations by 2 clients.
# 
# Idea is we have one pool for reservation and 2 clients want to claim as much as possible. A situation where one client
# claims all
# 
# Is undesirable. 

class CassandraTests(unittest.TestCase):

    def tearDown(self):
        session = get_cassandra_session()
        
        query_select = "SELECT book_status_id FROM sampledata.book_status;"
        rows = session.execute(query_select)

        for row in rows:
            query_update = "UPDATE sampledata.book_status SET status = 'free', user = 'free' WHERE book_status_id = %s;"
            session.execute(query_update, (row.book_status_id,))

    def test_1(self):
        session = get_cassandra_session()
                
        success = True
        
        for _ in range(1, 10):
            try:
                get_all_books(session)
            except:
                success = False
                break


        self.assertTrue(success)
    
    def test_2(self):
        users = []
        sessions = []
        for i in range(1, 3):
            users.append("User" + str(i))
            sessions.append(get_cassandra_session())
        
        operations = ["reserve", "check_available"]
        success = True
        
        for _ in range(1, 10):
            for uid, user in enumerate(users):
                try:
                    action = random.choice(operations)
                    if action == "reserve":
                        available_book_ids = available_books_id(sessions[uid])
                        if available_book_ids:
                            book_id = random.choice(available_book_ids)
                            add_reservation(user, sessions[uid], book_id)
                    elif action == "check_available":
                        available_books(sessions[uid])
                except:
                    success = False
                    break

        
        self.assertTrue(success)
        
    def test_3(self):
        users = []
        sessions = []
        for i in range(1, 3):
            users.append("User" + str(i))
            sessions.append(get_cassandra_session())
        
        success = True
        
        try:
            while True:
                available_book_ids = available_books_id(sessions[0])  
                if not available_book_ids:
                    break  
                
                for uid, user in enumerate(users):
                    for book_id in available_book_ids:
                        try:
                            add_reservation(user, sessions[uid], book_id)
                        except Exception as e:
                            continue
        except:
            success = False


        self.assertEqual(len(available_books_id(sessions[0])), 0)
        self.assertTrue(success)
     

if __name__ == "__main__":
    unittest.main()