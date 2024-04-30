import os
import json
import logging,logging.handlers

from typing import Union,Optional
from enum import Enum
from fastapi import FastAPI,HTTPException,Request,status,Query,UploadFile,Header
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
from tabulate import tabulate

from cygenai_env import CyLangEnv
from cygenai_semantic import CySemanticDB
from cygenai_semantic_data import CyLangContext,CyLangLLMData,CyLangContextType,CyLangSourceType,CyLangSource,CyLangHistory,CyLangApp
from cygenai_llm import CyLangLLM,CyLangLLMType
from cygenai_speech_recognition import CyLangSpeechRecognition,CyLangSpeechRecognizerType
from cygenai_summ import CyLangLSumm
from embeddings import CyEmbeddingsModel
from document_loaders import CyDocumentLoaderType,CyDocumentLoader
from cygenai_utils import xor,clean_query,format_cursor,lista_a_json
from cryptography.fernet import Fernet

from db import CyLangDBFactory,CyDBAdapterEnum

g_data={}

def startup():

    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/sparklelang.json'

    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
        g_data['env']=env
        logging.info("startup...")
    else:
        logging.error('%s not exists. Please configure environment variable CYGENAI_CONFIG_PATH',config_file) 

    semanticDB=CySemanticDB(env)
    g_data['apps']=semanticDB.get_app_all()



def shutdown():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # do startup
    startup() 
    yield
    # do shutdown
    shutdown()

app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
def validation_exception_handler(request: Request, exc: Exception):
    # Change here to Logger
    return JSONResponse(
        status_code=500,
        content={
            "message": (
                f"Failed method {request.method} at URL {request.url}."
                f" Exception message is {exc!r}."
            )
        },
    )

@app.get("/")
def read_root():
    env=g_data['env']
    logging.info("get_version=" + env.get_config().get_version())
    return env.get_config().get_version()

@app.get("/apps")
def get_apps(email: Annotated[str, Header()],
             pwd: Annotated[str, Header()]
             ):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    login=semanticDB.login(email=email,pwd=pwd)
    if login==-1:
        raise HTTPException(status_code=401, detail="Invalid emal or password")
    return semanticDB.get_app_all()

@app.get("/apps/{name}")
def get_app(email: Annotated[str, Header()],pwd: Annotated[str, Header()],name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    login=semanticDB.login(email=email,pwd=pwd)
    if login==-1:
        raise HTTPException(status_code=401, detail="Invalid emal or password")
    return semanticDB.get_app(name)


@app.post("/apps/",status_code=status.HTTP_201_CREATED)
def add_app(email: Annotated[str, Header()],pwd: Annotated[str, Header()],app_name: str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    login=semanticDB.login(email=email,pwd=pwd)
    if login==-1:
        raise HTTPException(status_code=401, detail="Invalid emal or password")
    
    import uuid 
    app_key = 'CyLang-'+str(uuid.uuid4()) 

    app=semanticDB.get_app(name=app_name)
    if app is None:
        app=CyLangApp(name=app_name,app_key=app_key,owner=login)
        semanticDB.add_app(app)
    else:
        app.app_key=app_key
        semanticDB.renew_app_key(app)    

    g_data['apps']=semanticDB.get_app_all()
    return app

@app.delete("/apps/{name}",status_code=status.HTTP_204_NO_CONTENT)
def remove_app(email: Annotated[str, Header()],pwd: Annotated[str, Header()],name: str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    login=semanticDB.login(email=email,pwd=pwd)
    if login==-1:
        raise HTTPException(status_code=401, detail="Invalid emal or password")
    semanticDB.remove_app(name)
    g_data['apps']=semanticDB.get_app_all()
    


@app.get("/contexts")
def get_contexts(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")   
    
    return semanticDB.get_context_all()

@app.get("/contexts/{name}")
def get_context(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")   
    
    ctx=semanticDB.get_context(name)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Context not found")
    return semanticDB.get_context(name)

@app.get("/embeddings-types")
def get_embedding_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env']
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")   
    
    return semanticDB.get_embs_types()

@app.get("/context-types")
def get_context_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_context_types()


class Context (BaseModel):
    name:str
    chunk_size:int=1000
    chunk_overlap:int=0
    embeddings_model:CyEmbeddingsModel=CyEmbeddingsModel.HUGGING_FACE
    context_type:CyLangContextType=CyLangContextType.CHAT_BOT
    context_size:int=3
    chunk_threshold:float=0.65
    load_threshold:float=0.65
    chunk_weight:float=0.85
    load_weight:float=0.15
    history:bool=False


@app.post("/contexts/",status_code=status.HTTP_201_CREATED)
def create_context(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context: Context):
    ctx=CyLangContext(context.name,context.chunk_size,context.chunk_overlap,context.embeddings_model.value,context.context_type.value,
                       context_size=context.context_size,chunk_threshold=context.chunk_threshold,load_threshold=context.load_threshold,
                       chunk_weight=context.chunk_weight,load_weight=context.load_weight,history=context.history)
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    semanticDB.create_context(ctx)    
    return context

@app.delete("/contexts/{context_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_context(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id: int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    
    semanticDB.delete_context(id=context_id)
    return context_id

@app.get("/source-types")
def get_source_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_source_types()


@app.get("/sources/{context_id}")
def get_sources(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_source_all(context_id)


class Source(BaseModel):
    context_id:int
    name:str
    source_type:CyLangSourceType
    host:str
    port:int
    service_name:Union[str, None] = Field(default=None, title="service name (e.g. oracle)")
    database:Union[str, None] = Field(default=None, title="database")
    userId:str
    password:str

@app.post("/sources/",status_code=status.HTTP_201_CREATED)
def add_source(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],source: Source):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(source.context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
   
    key=env.get_config().get_security_config()['encryption_key']
    fernet = Fernet(key)
    source.password=fernet.encrypt(source.password.encode())

    source=CyLangSource(context_id=source.context_id,name=source.name,source_type_id=source.source_type.value,
                          host=source.host,port=source.port,service_name=source.service_name,data_base=source.database,
                          user_id=source.userId,password=source.password.decode())
    
    semanticDB.add_source(source)  
    return source

@app.get("/sources/{context_id}/{name}")
def get_source(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    ctx=semanticDB.get_context_by_id(context_id=context_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Context not found")
    source=semanticDB.get_source(context_id=context_id,name=name)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@app.delete("/sources/{context_id}/{name}",status_code=status.HTTP_204_NO_CONTENT)
def remove_source(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    if semanticDB.get_source(context_id,name) is None:
       raise HTTPException(status_code=404, detail="Source not found")     

    semanticDB.remove_source(context_id,name)
    return str(context_id)+";"+name


@app.get("/llms/{context_id}")
def get_llms(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    return semanticDB.get_llm_all(context_id)


@app.get("/llm-types")
def get_llm_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_llm_types()



class LLM(BaseModel):
    context_id:int
    name:str =Field(default=None, title="Name of LLM")
    llm_type:CyLangLLMType
    model:Union[str, None] = Field(default=None, title="Name of model. eg. gemini-pro, gpt-4, ....")
    temperature:Union[float,None] = Field(default=None, title="Temperature of model")
    prompt_template:Union[str, None] = Field(default=None, title="Template used for prompt")
    llm_model_args:Union[str, None] = Field(default=None, title="Additional args of model")
    task:Union[str, None] = Field(default=None, title="Task request to LLM")
    local:bool=False
    pt_pipeline:bool=False

@app.post("/llms/",status_code=status.HTTP_201_CREATED)
def add_llm(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],llm: LLM):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(llm.context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    llm=CyLangLLMData(context_id=llm.context_id,name=llm.name,llm_type_id=llm.llm_type.value,model_name=llm.model,
                       temperature=llm.temperature,prompt_template=llm.prompt_template,
                       model_args=llm.llm_model_args,task=llm.task,local=llm.local,pt_pipeline=llm.pt_pipeline)
    semanticDB.add_llm(llm)  
    return llm

@app.get("/llms/{context_id}/{name}")
def get_llm(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    ctx=semanticDB.get_context_by_id(context_id=context_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Context not found")
    llm=semanticDB.get_llm(context_id=context_id,name=name)
    if llm is None:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm

@app.delete("/llms/{context_id}/{name}",status_code=status.HTTP_204_NO_CONTENT)
def remove_llm(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,name:str):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    if semanticDB.get_llm(context_id,name) is None:
       raise HTTPException(status_code=404, detail="LLM not found")     

    semanticDB.remove_llm(context_id,name)
    return str(context_id)+";"+name

@app.get("/sessions")
def get_session(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    import uuid 
    
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    semanticDB.clean_history() 
      
    id = uuid.uuid4() 
    return id


class Query(BaseModel):
    query:str
    context_id:int
    session_id:str=Field(default=None, title="Session-id used for history")
    llm_name:str =Field(default=None, title="Name of LLM")
    source_name:str =Field(default=None, title="Name of Source")
    askdata_output_fmt:str =Field(default=None, title="Formato in output per askdata")


@app.post("/llm-query/",status_code=status.HTTP_200_OK)
def llm_query(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],query: Query):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)

    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")                 

    ctx=semanticDB.get_context_by_id(query.context_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Context not found") 

    if ctx.history and query.session_id is None:
        raise HTTPException(status_code=404, detail="You should set session_id for context with history") 
    
    #load history
    history_size=env.get_config().get_history_config()['size']
    history=[]
    
    if ctx.history:
        history=semanticDB.get_history(context_id=ctx.id,session_id=query.session_id,size=history_size)
    query_search=query.query    
    
    if history is not None:
        for his in history:
            query_search=query_search+' '+his.query
        history.reverse()    
    logging.info("query_search="+query_search)
    
    
    if query.llm_name is None:
        query.llm_name="default"

    llm_conf=semanticDB.get_llm(context_id=query.context_id,name=query.llm_name)
    if llm_conf is None:
        raise HTTPException(status_code=404, detail="LLM not found")    

    llm=CyLangLLM(CyLangLLMType(llm_conf.llm_type_id),model_name=llm_conf.model_name,temperature=llm_conf.temperature,
                            template=llm_conf.prompt_template,model_args=llm_conf.model_args,task=llm_conf.task,
                            local=llm_conf.local,pt_pipeline=llm_conf.pt_pipeline) 
    
    logging.info("query="+query.query)
    logging.debug("llm_conf="+str(llm_conf))
    logging.debug("llm_type="+str(llm.llm_type))
    logging.debug("llm_model_name="+str(llm.model_name))
    logging.debug("llm_temperature="+str(llm.temperature))
    logging.debug("llm_model_args="+str(llm.model_args))
    logging.debug("llm_task="+str(llm.task))
    logging.debug("llm_local="+str(llm.local))
    logging.debug("llm_ppt_pipeline="+str(llm.pt_pipeline))


    if llm.llm_type==CyLangLLMType.HUGGING_FACE and \
        (llm.task=='text-classification' or llm.task=='sentiment-analysis' or llm.task=='text-generation' or llm.task=='text2text-generation'):
        chunks=[]
    else:
        chunks=semanticDB.similarity_search(ctx,query_search)
   
    res = llm.invoke(contexts=chunks,query=query.query,hasHistory=ctx.history,history=history)
    if res is None:
        res="I don't know"
    else:
        if llm.pt_pipeline is True:
            res=json.dumps(res)
        else:
            res=res['text']     
    
    if ctx.history and ctx.context_type_id != CyLangContextType.ASK_DATA.value:
        semanticDB.add_history(CyLangHistory(context_id=ctx.id,session_id=query.session_id,
                                              query=query.query,answer=res))

    if ctx.context_type_id == CyLangContextType.ASK_DATA.value:
        
        if query.source_name is None:
            query.source_name="default"

        source=semanticDB.get_source(query.context_id,query.source_name)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found") 

        key=env.get_config().get_security_config()['encryption_key']
        fernet = Fernet(key)
        source.password=fernet.decrypt(source.password).decode()
        #logging.info("password="+str(source.password))
       
        if source.source_type_id==CyLangSourceType.ORACLE.value:
            db_config={"user": source.user_id,"password": source.password, "host": source.host, 
                       "port": source.port,  "service_name": source.service_name}
            db_conn=CyLangDBFactory().getDB(adapter=CyDBAdapterEnum.CXORACLE,config=db_config)  
        elif source.source_type_id==CyLangSourceType.POSTGRESQL.value:
            db_config={"user": source.user_id,"password": source.password, "host": source.host, 
                       "port": source.port,  "database": source.data_base}
            db_conn=CyLangDBFactory().getDB(adapter=CyDBAdapterEnum.PSYCOPG2,config=db_config)  
        elif source.source_type_id==CyLangSourceType.ORACLETHIN.value:
            db_config={"user": source.user_id,"password": source.password, "host": source.host, 
                       "port": source.port,  "service_name": source.service_name}
            db_conn=CyLangDBFactory().getDB(adapter=CyDBAdapterEnum.ORACLETHIN,config=db_config)      
        else:
            raise HTTPException(status_code=404, detail="SourceType not supported")     
       
        db_conn.connect()

        max_attempts = env.get_config().get_askdata_config()['query_max_attempts']
        attempts = 0
        error_occurred = True

        while attempts < max_attempts and error_occurred:
            try:
                logging.debug("exec query on db")
                sql =clean_query(res)

                logging.info("sql="+sql)

                if ctx.history and ctx.context_type_id :
                    semanticDB.add_history(CyLangHistory(context_id=ctx.id,session_id=query.session_id,
                                              query=query.query,answer=sql))

                res_sql = db_conn.execute_select_query(sql)
                
                error_occurred = False 
                logging.info(res_sql)
                logging.debug("error_occurred="+str(error_occurred))
            except Exception as e:
                logging.debug("attempts=" + str(attempts))
                #logging.info("RES_SQL="+str(res_sql))
                error_occurred = True
                logging.error(f"error: {e}")
                #qui va aggiunta la modifica del prompt template
                addition = "Please, consider you already answered the question with the following query: " +    res + " and the database raised the following error when it was executed: " + f"{e}"
                attempts += 1
                if attempts < max_attempts:
                    res = llm.invoke(contexts=chunks, query=query.query, addition=addition,hasHistory=ctx.history,history=history)['text']
                    
                else:
                    logging.info("Maximum number of attempts exceeded. Breaking the loop.")
        
        db_conn.disconnect()

        if not error_occurred:
            
            if query.askdata_output_fmt is not None:
                if  query.askdata_output_fmt=='html':
                    formatted_res_sql=format_cursor(res_sql)
                    res = tabulate(formatted_res_sql, tablefmt="html") 
                elif query.askdata_output_fmt=='JSON':
                    res=lista_a_json(res_sql)
                else:
                    res=json.dumps(res_sql)  
            else:
                    res=json.dumps(res_sql)           
        else:
            res = "There was some problems during SQL query execution"

    return res

class LoadFolder(BaseModel):
    context_id:int
    folder:str
    parent_path:str=Field(default=None, title="Parent Path")


@app.post("/load-folders/",status_code=status.HTTP_201_CREATED)
def create_folder(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],folder: LoadFolder):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(folder.context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(folder.context_id)
    if not os.path.exists(ctx_folder):
        os.makedirs(ctx_folder)

    if folder.parent_path is None:
        folder_path=ctx_folder+"/"+folder.folder
    else:
        folder_path=ctx_folder+"/"+folder.parent_path+"/"+folder.folder
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path

@app.get("/load-folders/{context_id}")
def get_folder_list(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,folder:str=None):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(context_id)
    if not os.path.exists(ctx_folder):
         raise HTTPException(status_code=404, detail="Context folder not found")

    if folder is None:
        folder_path=ctx_folder
    else:
        folder_path=ctx_folder+"/"+folder

    return os.listdir(folder_path)

@app.delete("/load-folders/{context_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_folder(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,folder:str=None):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(context_id)
    if not os.path.exists(ctx_folder):
         raise HTTPException(status_code=404, detail="Context folder not found")

    if folder is None:
        folder_path=ctx_folder
    else:
        folder_path=ctx_folder+"/"+folder

    os.rmdir(folder_path)
    return folder_path


import shutil

@app.post("/load-files/{context_id}",status_code=status.HTTP_201_CREATED)
def upload_file(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],file:UploadFile,context_id:int,folderPath:str=None):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")    

    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")

    file_path=load_root_folder+"/ctx_"+str(context_id)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if folderPath is not None:
        file_path=file_path+'/'+folderPath
    file_path=file_path+'/'+file.filename    
   
    #contents = file.file.read()
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        # with open(file_path, 'wb') as f:
        #     f.write(contents)
    
    except Exception:
        raise HTTPException(status_code=500, detail="There was an error uploading the file")  
    finally:
        file.file.close()

    return {"filename": file_path}

class LoadFile(BaseModel):
    context_id:int
    file_path:str


@app.get("/load-files/{context_id}")
def get_file(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int,file_path:str):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(context_id)
    if not os.path.exists(ctx_folder):
         raise HTTPException(status_code=404, detail="Context folder not found")

    file_path=ctx_folder+"/"+file_path

    import ntpath
    head, tail = ntpath.split(file_path)
    file_name=tail or head

    logging.info("file_path="+file_path)
    logging.info("file_name="+file_name)
    
    from fastapi.responses import FileResponse
    return FileResponse(file_path, media_type='application/octet-stream',filename=file_name)


@app.delete("/load-files/",status_code=status.HTTP_204_NO_CONTENT)
def remove_file(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],load_file:LoadFile):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(load_file.context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(load_file.context_id)
    if not os.path.exists(ctx_folder):
         raise HTTPException(status_code=404, detail="Context folder not found")

    path=ctx_folder+'/'+load_file.file_path

    logging.info("file path="+path)
    if not os.path.exists(path):
       raise HTTPException(status_code=404, detail="File path="+path+" not found")
    
    os.remove(path)
    return path


@app.get("/load-types")
def get_load_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    return semanticDB.get_load_types()

class Load(BaseModel):
    context_id:int
    load_path:str
    load_type:CyDocumentLoaderType
    name:str
    content:str


@app.post("/loads/",status_code=status.HTTP_201_CREATED)
def add_load(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],load: Load):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")

    file_path=load_root_folder+"/ctx_"+str(load.context_id)+'/'+load.load_path
    logging.info("file_path="+file_path)

    semanticDB.add_load(context_id=load.context_id,load_type=load.load_type,name=load.name,
                        content=load.content,path=file_path,wait=False)
    return load

@app.get("/context-loads/{contex_id}")
def get_loads_by_context(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],context_id:int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_load_all(context_id)

@app.get("/loads/{load_id}")
def get_load(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],load_id:int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    load=semanticDB.get_load_by_id(load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")  
    return semanticDB.get_load_by_id(load_id)

@app.delete("/loads/{load_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_load(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],load_id:int):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    load=semanticDB.get_load_by_id(load_id)
    if load is None:
        raise HTTPException(status_code=404, detail="Load not found")   
    
    semanticDB.remove_load(load_id)
    return str(load_id)

@app.get("/speech-recognizer-types")
def get_speech_recognizer_types(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()]):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  

    return semanticDB.get_speech_recognizer_types()


@app.post("/speech-recognize/{context_id}/{speech_recognizer_type}",status_code=status.HTTP_200_OK)
def speech_recognize(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],
                file:UploadFile,context_id:int,speech_recognizer_type:int,
                folderPath:str=None,language:str=None):
    env=g_data['env'] 
    
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")    

    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")

    file_path=load_root_folder+"/ctx_"+str(context_id)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if folderPath is not None:
        file_path=file_path+'/'+folderPath
    file_path=file_path+'/'+file.filename    
   
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    
    except Exception:
        raise HTTPException(status_code=500, detail="There was an error uploading the file")  
    finally:
        file.file.close()

    # recognize
    text_rcgn=""
    if language is None:
        text_rcgn=CyLangSpeechRecognition(speech_type=speech_recognizer_type).recognize(file_path=file_path)
    else:
        text_rcgn=CyLangSpeechRecognition(speech_type=speech_recognizer_type).recognize(file_path=file_path,language=language)

    # delete file
    os.remove(file_path)    

    return {"text_rcgn": text_rcgn}

class Doc(BaseModel):
    doc_path:str
    load_type:CyDocumentLoaderType
    
class Summ(BaseModel):
    context_id:int
    llm_name:str
    summ_type:CyLangLLMType
    docs:list[Doc]   

@app.post("/summ/",status_code=status.HTTP_200_OK)
def summ_docs(app_name: Annotated[str, Header()],app_key: Annotated[str, Header()],summ: Summ):
    env=g_data['env'] 
    semanticDB=CySemanticDB(env)
    if not semanticDB.check_app_key(apps=g_data['apps'],app_name=app_name,app_key=app_key):
        raise HTTPException(status_code=403, detail="Access denied")  
    
    if semanticDB.get_context_by_id(summ.context_id) is None:
       raise HTTPException(status_code=404, detail="Context not found")     
    
    load_root_folder=env.get_config().get_load_config()['root_folder']
    if load_root_folder is None:
        raise HTTPException(status_code=404, detail="You shoud configure load root_folder")
    
    ctx_folder=load_root_folder+"/ctx_"+str(summ.context_id)
    if not os.path.exists(ctx_folder):
         raise HTTPException(status_code=404, detail="Context folder not found")
    
    if summ.llm_name is None:
       summ.llm_name="default"

    llm_conf=semanticDB.get_llm(context_id=summ.context_id,name=summ.llm_name)
    if llm_conf is None:
        raise HTTPException(status_code=404, detail="LLM not found")    

    llm_sum=CyLangLSumm(CyLangLLMType(llm_conf.llm_type_id),model_name=llm_conf.model_name,temperature=llm_conf.temperature,
                            template=llm_conf.prompt_template) 
    docs=None
    
    for doc in summ.docs:
        
        if doc.load_type==CyDocumentLoaderType.WEB:
            doc_path=doc.doc_path 
        else:         
            doc_path=ctx_folder+'/'+doc.doc_path
        logging.info("doc_path:"+doc_path)
        
        loader=CyDocumentLoader(doc.load_type,doc_path)
        if docs is None:
            docs=loader.load()
        else:
            docs.extend(loader.load())    

    res=llm_sum.invoke(docs)

    if res is None:
        res="There are some problems"
    else:
        res=res['output_text'] 

    return res