# cassandra-app
Simple library app using python and cassandra with 3 nodes (+1 for app).

docker-compose up --build

python initialize_cassandra.py

docker exec -it cassandra-cassandra-node1-1 cqlsh cassandra-node1 9042

 DESCRIBE KEYSPACES;

 
docker-compose down
