from enum import Enum

from .pg_connector import CyPgConnector
from .oracle_connector import CyOracleConnector
from .db_if import CyLangDB


class CyDBAdapterEnum(Enum):
    PSYCOPG2=1
    CXORACLE=2


class CyLangDBFactory():
    def getDB(self,adapter:CyDBAdapterEnum,config:dict)->CyLangDB:
        if adapter==CyDBAdapterEnum.PSYCOPG2:
             _impl=CyPgConnector(config)
        elif adapter==CyDBAdapterEnum.CXORACLE:
             _impl=CyOracleConnector(config)
        else:
            _impl = None
            raise ValueError(adapter)
        return _impl  