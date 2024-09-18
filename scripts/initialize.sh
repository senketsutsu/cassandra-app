echo "Waiting for Cassandra..."
until $(docker exec cassandra-cassandra-node1-1 nodetool status | grep "UN" > /dev/null); do 
  sleep 5; 
done
echo "Cassandra is ready."

echo "Initializing DB..."
sleep 10
docker exec cassandra-cassandra-node1-1 cqlsh -f /scripts/init-db.cql
echo "done"
