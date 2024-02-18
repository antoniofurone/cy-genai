from abc import ABC, abstractmethod

class CyLangData(ABC):
    @abstractmethod
    def get_table(self)->str:
        pass
    @abstractmethod
    def get_cols(self)->list[str]:
        pass    
    @abstractmethod
    def get_values(self)->list:
        pass    
    @abstractmethod
    def get_schema(self)->str:
        pass        

class CyLangDB(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def execute_command(self,command:str):
        pass  

    @abstractmethod    
    def execute_commands(self,commands:list[str]):
        pass
 
    @abstractmethod
    def execute_command_values(self,data:CyLangData):
        pass

    @abstractmethod
    def execute_query(self,query:str,log_query:bool=True):   
        pass   

    @abstractmethod    
    def disconnect(self):
        pass

    @abstractmethod    
    def execute_select_query(self, query: str, log_query: bool = True) -> list:
        pass
