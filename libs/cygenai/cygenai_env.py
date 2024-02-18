import json
import logging,logging.handlers
from db import CyLangDB,CyDBAdapterEnum,CyLangDBFactory

class CyLangConfig:
    def __init__(self,configFile) -> None:
        self.__configFile=configFile
        self.__load()

    def __load(self)->None:
        with open(self.__configFile, 'r') as config_file:
            self.__config_data=json.load(config_file)
    
    def get_version(self)->str:
        return self.__config_data['version']
    
    def get_logging_config(self)->str:
        return self.__config_data['logging']

    def get_semantic_db_config(self)->dict:
        return self.__config_data['semantic_db']
    
    def get_embeddings_config(self)->dict:
        return self.__config_data['embeddings']
    
    def get_load_config(self)->dict:
        return self.__config_data['load']

    def get_api_server_config(self)->dict:
        return self.__config_data['api_server']

    def get_web_server_config(self)->dict:
        return self.__config_data['web_server']

    def get_secret_config(self)->dict:
        return self.__config_data['secret']

    def get_chatbot_config(self)->dict:
        return self.__config_data['chatbot']

    def get_askdata_config(self)->dict:
        return self.__config_data['askdata']
    
    def get(self,key:str)->dict:
        return self.__config_data[key]

class CyLangEnv:
    def __init__(self,configFile:str):
        self.__configPath=configFile
        self.__config=CyLangConfig(self.__configPath)
        self.__set_logger(self.__config.get_logging_config())
    
    
    def get_config(self)->CyLangConfig:
        return self.__config

    def __set_logger(self,logging_config:dict):

        logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s') 
        rootLogger = logging.getLogger()
        
        fileHandler = logging.handlers.RotatingFileHandler(logging_config['fileName'],maxBytes=(1024*1024), backupCount=7,encoding='utf-8')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
    
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
    
        logger = logging.getLogger()

        if logging_config['level']=="INFO":
            logging_level=logging.INFO
        elif  logging_config['level']=="DEBUG":
            logging_level=logging.DEBUG
        elif  logging_config['level']=="ERROR":
            logging_level=logging.ERROR
        elif  logging_config['level']=="WARN":
            logging_level=logging.WARN  
        elif  logging_config['level']=="WARNING":
            logging_level=logging.WARNING          
        elif  logging_config['level']=="NOTSET":
            logging_level=logging.NOTSET    
        else:
            logging_level=logging.INFO
        
        logger.setLevel(logging_level)
        

    def get_semantic_db_connector(self)->CyLangDB:
        return CyLangDBFactory().getDB(CyDBAdapterEnum.PSYCOPG2,self.__config.get_semantic_db_config())   

    def create_semantic_db(self):
        dbConnector=self.get_semantic_db_connector()
        dbConnector.connect()
        
        logging.info("create table cy_context")

        cmd="""CREATE TABLE IF NOT EXISTS cy_context(
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
                CONSTRAINT fk_ctx_embs_model
                    FOREIGN KEY(embedding_model) 
                    REFERENCES cy_embs_types(id)
                    ,
                CONSTRAINT fk_ctx_type
                    FOREIGN KEY(context_type) 
                    REFERENCES cy_context_types(id)
                    )    
                    """
        dbConnector.execute_command(cmd)

        logging.info("create table cy_llm")
        cmd="""CREATE TABLE IF NOT EXISTS cy_llm(
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
                    )   
                """
        dbConnector.execute_command(cmd)

        logging.info("create table cy_load")
        cmd="""CREATE TABLE IF NOT EXISTS cy_load(
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
                )    
                """
        dbConnector.execute_command(cmd)

        logging.info("create table cy_load_trace")
        cmd="""CREATE TABLE IF NOT EXISTS cy_load_trace(
                load_id integer not null,
                time_stamp timestamp not null,
                step varchar(200) not null,
                CONSTRAINT fk_load_trace_load_id
                    FOREIGN KEY(load_id) 
                    REFERENCES cy_load(id))"""
        dbConnector.execute_command(cmd)


        logging.info("create table cy_chunk")
        cmd="""CREATE TABLE IF NOT EXISTS cy_chunk(
                id SERIAL PRIMARY KEY,
                load_id integer,
                content text,
                metadata text,
                embedding vector(1600),
                CONSTRAINT fk_chunk_load_id
                    FOREIGN KEY(load_id) 
                    REFERENCES cy_load(id)
                )"""
        dbConnector.execute_command(cmd)

        logging.info("create table cy_source")
        cmd="""CREATE TABLE IF NOT EXISTS cy_source(
                context_id integer not null,
                name varchar(20) not null,
                type_id smallint not null,
                userid varchar(20) not null,
                pwd varchar(20) not null,
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
                )"""
        dbConnector.execute_command(cmd)

        logging.info("create cosine idx on cy_chunk")
        cmd="""CREATE INDEX  ON cy_chunk
              USING hnsw(embedding vector_cosine_ops)
              WITH (m = 24, ef_construction = 100)"""
        dbConnector.execute_command(cmd)

        logging.info("create cosine idx on cy_load")
        cmd="""CREATE INDEX  ON cy_load
              USING hnsw(embedding vector_cosine_ops)
              WITH (m = 24, ef_construction = 100)"""
        dbConnector.execute_command(cmd)

        dbConnector.disconnect()

    def desctroy_semantic_db(self):
        dbConnector=self.get_semantic_db_connector()
        dbConnector.connect()
        
        logging.info("drop table cy_source")
        cmd="""DROP TABLE IF EXISTS cy_source"""
        dbConnector.execute_command(cmd)

        logging.info("drop table cy_chunk")
        cmd="""DROP TABLE IF EXISTS cy_chunk"""
        dbConnector.execute_command(cmd)

        logging.info("drop table cy_llm")
        cmd="""DROP TABLE IF EXISTS cy_llm"""
        dbConnector.execute_command(cmd)

        logging.info("drop table cy_load_trace")
        cmd="""DROP TABLE IF EXISTS cy_load_trace"""
        dbConnector.execute_command(cmd)

        logging.info("drop table cy_load")
        cmd="""DROP TABLE IF EXISTS cy_load"""
        dbConnector.execute_command(cmd)

        logging.info("drop table cy_context")
        cmd="""DROP TABLE IF EXISTS cy_context"""
        dbConnector.execute_command(cmd)
        
        dbConnector.disconnect()

