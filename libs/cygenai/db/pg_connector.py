from .db_if import CyLangDB,CyLangData

import logging
import psycopg2
from psycopg2 import sql
import psycopg2.extras as extras

class CyPgConnector(CyLangDB):
    def __init__(self,config:dict):
        self.__database=config["database"]
        self.__user=config["user"]
        self.__host=config["host"]
        self.__password=config["password"]
        self.__port=config["port"]
    
    def connect(self):
        self.__conn = psycopg2.connect(database = self.__database, user = self.__user, host= self.__host,password = self.__password,
                        port = self.__port)

    def execute_command(self,command:str):
        try:
            
            cur = self.__conn.cursor()
            # Execute a command: create datacamp_courses table
            logging.info(command)
            cur.execute(command)
            # Make the changes to the database persistent
            self.__conn.commit()  
        
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error: %s" % error)
            self.__conn.rollback()     
            raise   


    def execute_commands(self,commands:list[str]):
        
        try:
            cur = self.__conn.cursor()
            for cmd in commands:
                logging.info(cmd)
                cur.execute(cmd)

                self.__conn.commit()  

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error: %s" % error)
            self.__conn.rollback()    
            raise    


    def execute_command_values(self,data:CyLangData):
        
        try:
            cur = self.__conn.cursor()

            cmd = sql.SQL("INSERT INTO {table}({cols}) values %s")\
                .format(table=sql.Identifier(data.get_schema(), data.get_table()),cols=sql.SQL(", ")\
                .join(map(sql.Identifier, data.get_cols())))
            
            logging.info(cmd.as_string(self.__conn))
            
            extras.execute_values(cur, cmd, data.get_values())
            
            self.__conn.commit()
            
            logging.info("insert is ok")

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error: %s" % error)
            self.__conn.rollback()
            raise

    def execute_query(self,query:str,log_query:bool=True):   
        
        try:
            cur = self.__conn.cursor()  
            if log_query:
                logging.info(query)
            cur.execute(query)
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error: %s" % error)
            raise
                  
        return cur   
    
    def execute_select_query(self, query: str, log_query: bool = False) -> list:
        """
        Esegue una query di selezione sul database e restituisce i risultati.

        :param query: La query di selezione SQL.
        :param log_query: Se True, registra la query nei log.
        :return: Una lista di tuple rappresentanti le righe restituite dalla query.
        """
        try:
            cur = self.__conn.cursor()
            if log_query:
                logging.info(query)

            cur.execute(query)
            result = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error: %s" % error)
            raise
                  
        return result

    def disconnect(self):
        self.__conn.close()    