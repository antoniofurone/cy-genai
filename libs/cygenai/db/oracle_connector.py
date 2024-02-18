import logging
import cx_Oracle
from .db_if import CyLangData,CyLangDB


class CyOracleConnector(CyLangDB):
    def __init__(self, config: dict):
        self.__user = config["user"]
        self.__password = config["password"]
        self.__dsn = cx_Oracle.makedsn(config["host"], config["port"], service_name=config["service_name"])

    def connect(self):
        
        try:
            self.__conn = cx_Oracle.connect(user=self.__user, password=self.__password, dsn=self.__dsn)
        except cx_Oracle.Error as error:
            logging.error("Error connecting to Oracle: %s", error)
            raise

    def execute_command(self, command: str):
        try:
            cur = self.__conn.cursor()
            logging.info(command)
            cur.execute(command)
            self.__conn.commit()
        except cx_Oracle.Error as error:
            logging.error("Error executing command in Oracle: %s", error)
            self.__conn.rollback()
            raise

    def execute_commands(self, commands: list[str]):
        try:
            cur = self.__conn.cursor()
            for cmd in commands:
                logging.info(cmd)
                cur.execute(cmd)
                self.__conn.commit()
        except cx_Oracle.Error as error:
            logging.error("Error executing commands in Oracle: %s", error)
            self.__conn.rollback()
            raise

    def execute_command_values(self, data: CyLangData):
        try:
            cur = self.__conn.cursor()
            cmd = "INSERT INTO {}({}) VALUES ({})".format(
                data.get_table(), ", ".join(data.get_cols()), ", ".join("%s" for _ in data.get_cols()))
            logging.info(cmd)
            cur.executemany(cmd, data.get_values())
            self.__conn.commit()
            logging.info("Insert is ok")
        except cx_Oracle.Error as error:
            logging.error("Error executing command with values in Oracle: %s", error)
            self.__conn.rollback()
            raise

    def execute_query(self, query: str, log_query: bool = True):
        try:
            cur = self.__conn.cursor()
            if log_query:
                logging.info(query)
            cur.execute(query)
        except cx_Oracle.Error as error:
            logging.error("Error executing query in Oracle: %s", error)
            raise

    def execute_select_query(self, query: str, log_query: bool = True) -> list:
        try:
            cur = self.__conn.cursor()
            if log_query:
                logging.info(query)
            cur.execute(query)
            column_names = [desc[0] for desc in cur.description]
            result = [column_names] + cur.fetchall()
            return result
        except cx_Oracle.Error as error:
            logging.error("Error executing select query in Oracle: %s", error)
            raise

    def disconnect(self):
        try:
            self.__conn.close()
            logging.info("Disconnected from Oracle database")
        except cx_Oracle.Error as error:
            logging.error("Error disconnecting from Oracle: %s", error)
            raise


    
