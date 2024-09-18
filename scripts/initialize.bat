@echo off
echo Waiting for Cassandra...

:wait_for_cassandra
docker exec cassandra-cassandra-node1-1 nodetool status | find "UN" >nul
if %errorlevel% neq 0 (
    timeout /t 5 /nobreak >nul
    goto wait_for_cassandra
)
echo Cassandra is ready.

echo Copying CQL file to container...
docker cp init-db.cql cassandra-cassandra-node1-1:/init-db.cql

echo Initializing DB...
docker exec cassandra-cassandra-node1-1 cqlsh -f /init-db.cql
echo Database initialization complete.
