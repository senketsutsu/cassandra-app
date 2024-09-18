# Library app
Simple library app using Python and Cassandra with 3 nodes (+1 for app).

The app has currently 5 books, but it can be simply modified in the  init-db.cql file (but remember to also add the book to the book_status).

The app allows:
- showing all books and who reserved them
- showing all available books
- showing current user reservations
- updating reservation (change from one book to another)
- deleting reservation (give back the book)


To run the Cassandra:
```sh
docker-compose up --build
```

Wait for the app to be ready (you can look at the current status on the docker app). 
The app will be available at: http://localhost:5555/

To close:
```sh
docker-compose down
```
## Run tests
To run the tests:
```sh
python tests.py
```

The tests take time due to the large number of iterations (10 000).

They test:
- if you can quickly see all books multiple times
- multiple users (3) try making random (reserve or see available) operations multiple times
- multiple users (3)  try to reserve as many as possible books
