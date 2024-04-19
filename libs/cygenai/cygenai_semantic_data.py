from enum import Enum
import logging,logging.handlers

from db import CyLangData

class CyLangContextType(Enum):
    CHAT_BOT=1
    ASK_DATA=2
    GENAI_TASKS=3

class CyLangSourceType(Enum):
    ORACLE=1
    POSTGRESQL=2
    ORACLETHIN=3

class CyLangChunk():
    def __init__(self,content:str,metadata:dict,
                 embeddings:list[float]=None,similarity:float=0,id:int=0,load_id:int=0):
        self.content=content
        self.metadata=metadata
        self.embeddings=embeddings
        self.similarity=similarity
        self.id=id
        self.load_id=load_id

    def __str__(self):
        return "["+str(self.id)+";"+str(self.load_id)+";"+str(self.similarity)+"]"

class CyLangChunks(CyLangData):
    def __init__(self,load_id:int,chunks:list[CyLangChunk],id:int=0):
        self.id=id
        self.load_id=load_id
        self.chunks=chunks
       
    def get_table(self)->str:
        return "cy_chunk"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['load_id','metadata','content','embedding']
    
    def get_values(self)->list:
        ret=[]
        for chunk in self.chunks:
            ret.append((self.load_id,str(chunk.metadata),chunk.content,chunk.embeddings))
        return ret


class CyLangLoad(CyLangData):
    def __init__(self,name:str='',context_id:int=0,content:str='',
                 embeddings:list[float]=None,id:int=0,similarity:float=0,path:str='',load_type_id:int=None,
                 status:str='Running',load_type_name:str=None):
        self.id=id
        self.name=name
        self.context_id=context_id
        self.content=content
        self.embeddings=embeddings
        self.similarity=similarity
        self.path=path
        self.load_type_id=load_type_id
        self.status=status
        self.load_type_name=load_type_name

    def get_table(self)->str:
        return "cy_load"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['load_name','context_id','content','embedding','path','load_type','status']
    
    def get_values(self)->list:
        return [(self.name,self.context_id,self.content,self.embeddings,self.path,self.load_type_id,self.status)]

    def __str__(self):
        return "["+str(self.id)+";"+str(self.similarity)+"]"

class CyLangHistory(CyLangData):
    def __init__(self,context_id:str,session_id:str,
                 query:str,answer:str):
        self.context_id=context_id
        self.session_id=session_id
        self.query=query
        self.answer=answer
      
    def get_table(self)->str:
        return "cy_history"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['context_id','session_id','query','answer']

    def get_values(self)->list:
        return [(self.context_id,self.session_id,self.query,self.answer)]
    
class CyLangApp(CyLangData):
    def __init__(self,name:str,app_key:str,owner:str):
        self.name=name
        self.app_key=app_key
        self.owner=owner

    def get_table(self)->str:
        return "cy_app"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['name','app_key','owner']

    def get_values(self)->list:
        return [(self.name,self.app_key,self.owner)]

class CyLangSource(CyLangData):
    def __init__(self,context_id:str,name:str,source_type_id:int,
                host:str,port:int,
                user_id:str,password:str,
                data_base:str=None,
                service_name:str=None,
                source_type_name:str=None):
        self.context_id=context_id
        self.name=name
        self.source_type_id=source_type_id
        self.host=host
        self.port=port
        self.data_base=data_base
        self.service_name=service_name
        self.user_id=user_id
        self.password=password
        self.source_type_name=source_type_name

    def get_table(self)->str:
        return "cy_source"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['context_id','name','type_id','userid','pwd','host','port','service_name','database']

    def get_values(self)->list:
        return [(self.context_id,self.name,self.source_type_id,self.user_id,self.password,self.host,self.port,self.service_name,self.data_base)]
    

class CyLangLLMData(CyLangData):
    def __init__(self,context_id:int,name:str,llm_type_id:int,
                 model_name:str=None,temperature:float=None,
                 prompt_template:str=None,llm_type_name:str=None,
                 model_args:str=None,task:str=None,
                 local:bool=False,pt_pipeline:bool=False):
        self.context_id=context_id
        self.name=name
        self.llm_type_id=llm_type_id
        self.model_name=model_name
        self.temperature=temperature
        self.prompt_template=prompt_template
        self.llm_type_name=llm_type_name
        self.model_args=model_args
        self.task=task
        self.local=local
        self.pt_pipeline=pt_pipeline
      
    def get_table(self)->str:
        return "cy_llm"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['context_id','name','llm_type','model_name','temperature','template','model_args','task','local','pt_pipeline']
    
    def get_values(self)->list:
        return [(self.context_id,self.name,self.llm_type_id,self.model_name,self.temperature,
                 self.prompt_template,self.model_args,self.task,self.local,self.pt_pipeline)]
       
    def __str__(self):
        return "["+str(self.context_id)+";"+self.name+";"+str(self.llm_type_id)+";"+(self.model_name or "")+";"+str(self.temperature or "")+"]"    

class CyLangContext(CyLangData):
    def __init__(self,name:str,chunk_size:int, chunk_overlap:int,
                embeddings_model_id:int,context_type_id:int,id:int=0,context_size:int=5,
                chunk_threshold:float=0.75,load_threshold:float=0.75,
                chunk_weight:float=0.8,load_weight:float=0.2,history:bool=False,session_id:str=None,
                embeddings_model_name:str=None,context_type_name:str=None
                ):
        self.id=id
        self.name=name
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap
        self.embeddings_model_id=embeddings_model_id
        self.context_type_id=context_type_id
        self.context_size=context_size
        self.chunk_threshold=chunk_threshold
        self.load_threshold=load_threshold
        self.chunk_weight=chunk_weight
        self.load_weight=load_weight
        self.history=history
        self.embeddings_model_name=embeddings_model_name
        self.context_type_name=context_type_name
        
        
    def get_table(self)->str:
        return "cy_context"    
    
    def get_schema(self)->str:
        return "public"   

    def get_cols(self)->list:
        return ['context_name','chunk_size','chunk_overlap','embedding_model','context_type','context_size',
                'chunk_threshold','load_threshold','chunk_weight','load_weight','history']
    
    def get_values(self)->list:
        return [(self.name,self.chunk_size,self.chunk_overlap,self.embeddings_model_id,self.context_type_id,self.context_size,
                 self.chunk_threshold,self.load_threshold,self.chunk_weight,self.load_weight,self.history)]
       
    def __str__(self):
        return "["+str(self.id)+";"+self.name+";"+str(self.chunk_size)+";"+str(self.chunk_overlap)+";"+str(self.embeddings_model_id)+";"+\
            str(self.context_type_id)+";"+str(self.context_size)+";"+str(self.chunk_threshold)+";"+str(self.load_threshold)+";"+\
            str(self.chunk_weight)+";"+str(self.load_weight)+";"+str(self.history)+"]"

