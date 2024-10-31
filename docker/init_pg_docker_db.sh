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
    # cy_embs_types
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_embs_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_embs_types(id,name) values (1,'Google Vertex AI');"
    psql -U cygenai -d cygenaidb -c "insert into cy_embs_types(id,name) values (2,'Open AI');"
    psql -U cygenai -d cygenaidb -c "insert into cy_embs_types(id,name) values (3,'Hugging Face');"


    # cy_context_types
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_context_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_context_types(id,name) values (1,'Chat Bot');"
    psql -U cygenai -d cygenaidb -c "insert into cy_context_types(id,name) values (2,'Ask Data');"
    psql -U cygenai -d cygenaidb -c "insert into cy_context_types(id,name) values (3,'GenAI Tasks');"

    # cy_llm_types
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_llm_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_llm_types(id,name) values (1,'Chat Open AI');"
    psql -U cygenai -d cygenaidb -c "insert into cy_llm_types(id,name) values (2,'Open AI');"
    psql -U cygenai -d cygenaidb -c "insert into cy_llm_types(id,name) values (3,'Google Vertex AI');"
    psql -U cygenai -d cygenaidb -c "insert into cy_llm_types(id,name) values (4,'Hugging Face');"

    # cy_load_types
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_load_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (1,'Pdf');"
    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (2,'File Directory');"
    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (3,'Csv');"
    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (4,'Unstructuted Html');"
    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (5,'Bs Html');"
    psql -U cygenai -d cygenaidb -c "insert into cy_load_types(id,name) values (6,'Web');"

    # cy_source_types
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_source_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_source_types(id,name) values (1,'Oracle');"
    psql -U cygenai -d cygenaidb -c "insert into cy_source_types(id,name) values (2,'PostgreSQL');"
    psql -U cygenai -d cygenaidb -c "insert into cy_source_types(id,name) values (3,'OracleThin');"

    # cy_speech_recognizer
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_speech_recognizer_types(id smallint PRIMARY KEY,name varchar(30) not null);"

    psql -U cygenai -d cygenaidb -c "insert into cy_speech_recognizer_types(id,name) values (1,'Whisper');"
    psql -U cygenai -d cygenaidb -c "insert into cy_speech_recognizer_types(id,name) values (2,'Google Cloud');"

    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_context(
                id SERIAL PRIMARY KEY,
                context_name varchar(20) not null unique,
                chunk_size integer not null,
                chunk_overlap integer not null,
                context_size integer not null,
                chunk_threshold double precision not null,
                load_threshold double precision not null,
                chunk_weight double precision not null,
                load_weight double precision not null,
                embedding_model smallint not null,
                context_type smallint not null,
                history boolean not null default false,
                CONSTRAINT fk_ctx_embs_model
                    FOREIGN KEY(embedding_model) 
                    REFERENCES cy_embs_types(id)
                    ,
                CONSTRAINT fk_ctx_type
                    FOREIGN KEY(context_type) 
                    REFERENCES cy_context_types(id)
                    );"

     psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_llm(
                context_id integer not null,
                name varchar(20) not null,
                llm_type integer not null,
                model_name varchar(50),
                temperature double precision,
                template text,
                model_args varchar(100),
                task varchar(50),
                local boolean not null default false,
                pt_pipeline boolean not null default false,
                PRIMARY KEY(context_id,name),
                CONSTRAINT fk_llm_context_id
                    FOREIGN KEY(context_id) 
                    REFERENCES cy_context(id)
                    ,
                CONSTRAINT fk_llm_type
                    FOREIGN KEY(llm_type) 
                    REFERENCES cy_llm_types(id)
                    );"

    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_load(
                id SERIAL PRIMARY KEY,
                context_id  integer,
                load_name varchar(30) not null unique,
                content text,
                status varchar(30) not null,
                path varchar(200) not null,
                load_type int not null,
                embedding vector(1600),
                CONSTRAINT fk_load_context_id
                    FOREIGN KEY(context_id) 
                    REFERENCES cy_context(id),
                CONSTRAINT fk_load_type
                    FOREIGN KEY(load_type) 
                    REFERENCES cy_load_types(id)
                );"
    
    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_load_trace(
                load_id integer not null,
                time_stamp timestamp not null,
                step varchar(200) not null,
                CONSTRAINT fk_load_trace_load_id
                    FOREIGN KEY(load_id) 
                    REFERENCES cy_load(id));"


    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_chunk(
                id SERIAL PRIMARY KEY,
                load_id integer,
                content text,
                metadata text,
                embedding vector(1600),
                CONSTRAINT fk_chunk_load_id
                    FOREIGN KEY(load_id) 
                    REFERENCES cy_load(id)
                );"

    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_source(
                context_id integer not null,
                name varchar(20) not null,
                type_id smallint not null,
                userid varchar(20) not null,
                pwd varchar(100) not null,
                host varchar(20) not null,
                port integer not null,
                service_name varchar(30),
                database varchar(30),
                PRIMARY KEY(context_id,name),
                CONSTRAINT fk_source_context_id
                    FOREIGN KEY(context_id) 
                    REFERENCES cy_context(id),
                CONSTRAINT fk_source_type
                    FOREIGN KEY(type_id) 
                    REFERENCES cy_source_types(id)    
                );"

    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_history(
                context_id  integer not null,
                session_id char(36) not null,
                query text not null,
                answer text not null,
                time_stamp timestamp not null default CURRENT_TIMESTAMP,
                CONSTRAINT fk_hist_context_id
                    FOREIGN KEY(context_id) 
                    REFERENCES cy_context(id)
            );"

   psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_user(
                id SERIAL PRIMARY KEY,
                email  	varchar(50) not null unique,
                pwd		varchar(100) not null,
                name   	varchar(50) not null,
                surname varchar(50) not null
            );"


    psql -U cygenai -d cygenaidb -c "CREATE TABLE IF NOT EXISTS cy_app(
                name  		varchar(30) not null PRIMARY KEY,
                app_key		varchar(50) not null,
                owner       integer not null,
                CONSTRAINT fk_app_owner
                    FOREIGN KEY(owner) 
                    REFERENCES cy_user(id)
            );"

    psql -U cygenai -d cygenaidb -c "CREATE INDEX  ON cy_chunk
              USING hnsw(embedding vector_cosine_ops)
              WITH (m = 24, ef_construction = 100);"

    psql -U cygenai -d cygenaidb -c "CREATE INDEX  ON cy_load
              USING hnsw(embedding vector_cosine_ops)
              WITH (m = 24, ef_construction = 100);"

else
    su postgres -c "pg_ctl -D /cy-genai-db/data -l /cy-genai-db/logs/serverlog.log start"
fi
exec tail -f /dev/null

