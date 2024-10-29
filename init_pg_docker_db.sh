#!/bin/sh
CONTAINER_FIRST_STARTUP="CONTAINER_FIRST_STARTUP"
#if [ ! -e /$CONTAINER_FIRST_STARTUP ]; then
    #touch /$CONTAINER_FIRST_STARTUP
if [ -z "$( ls -A '/cy-genai-db/data' )" ]; then    
    # place your script that you only want to run on first startup.
    chown postgres /cy-genai-db/data
    chown postgres /cy-genai-db/logs
    su postgres -c "initdb /cy-genai-db/data"
    su postgres -c "pg_ctl -D /cy-genai-db/data -l /cy-genai-db/logs/serverlog.log start"
    
    export POSTGRES_PASSWORD=postgres
    psql -U postgres -c "CREATE EXTENSION vector"
    psql -U postgres -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"

    psql -U postgres -c "CREATE USER cygenai WITH PASSWORD 'cygenai_dk';"
    psql -U postgres -c "CREATE DATABASE cygenaidb;"
    psql -U postgres -c "GRANT ALL ON DATABASE cygenaidb TO cygenai;"
    psql -U postgres -c "ALTER DATABASE cygenaidb OWNER TO cygenai;"

    psql -U postgres -d cygenaidb -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    export PGPASSWORD=cygenai_dk
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_embs_types(id smallint PRIMARY KEY,name varchar(30) not null);"
   

else
    su postgres -c "pg_ctl -D /cy-genai-db/data -l /cy-genai-db/logs/serverlog.log start"
fi
exec tail -f /dev/null

