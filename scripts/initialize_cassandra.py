from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time


def wait_for_cassandra(cluster):
    while True:
        try:
            session = cluster.connect()
            session.execute("SELECT release_version FROM system.local")
            print("Cassandra is ready!")
            break
        except Exception as e:
            print("Waiting for Cassandra to be ready...")
            time.sleep(5)




cluster = Cluster()
session = cluster.connect()

wait_for_cassandra(cluster)


session.execute("""
    CREATE KEYSPACE IF NOT EXISTS sampledata 
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};
""")


session.execute("USE sampledata;")

session.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INT PRIMARY KEY,
        title TEXT
    );
""")

session.execute("INSERT INTO books (book_id, title) VALUES (1, 'Cantebury tales');")
session.execute("INSERT INTO books (book_id, title) VALUES (2, 'Bible');")
session.execute("INSERT INTO books (book_id, title) VALUES (3, 'Dictionary');")
session.execute("INSERT INTO books (book_id, title) VALUES (4, 'Pride and Prjudice');")
session.execute("INSERT INTO books (book_id, title) VALUES (5, 'Winnie the Pooh');")

session.execute("""
    CREATE TABLE IF NOT EXISTS book_status (
        book_status_id INT PRIMARY KEY,
        title TEXT,
        status TEXT,
        user TEXT
    );
""")

session.execute("INSERT INTO book_status (book_status_id, title, status, user) VALUES (1, 'Cantebury tales', 'free', 'free');")
session.execute("INSERT INTO book_status (book_status_id, title, status, user) VALUES (2, 'Bible', 'free', 'free');")
session.execute("INSERT INTO book_status (book_status_id, title, status, user) VALUES (3, 'Dictionary', 'free', 'free');")
session.execute("INSERT INTO book_status (book_status_id, title, status, user) VALUES (4, 'Pride and Prjudice', 'free', 'free');")
session.execute("INSERT INTO book_status (book_status_id, title, status, user) VALUES (5, 'Winnie the Pooh', 'free', 'free');")

print("Database initialization complete!")
