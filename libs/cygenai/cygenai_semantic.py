from enum import Enum
import traceback
import logging,logging.handlers


from cygenai_env import CyLangEnv
from text_splitter import CyTextSplitter
from embeddings import CyEmbeddings,CyEmbeddingsBatch,CyEmbeddingsModel
from cygenai_semantic_data import CyLangContext,CyLangLoad,CyLangChunk,CyLangChunks,CyLangLLMData,CyLangSource,CyLangHistory
from cygenai_semantic_dao import CyLangContextDao,CyLangLLMDao,CyLangLoadDao,CyLangChunkDao,CyLangSourceDao,CyLangHistoryDao
from cygenai_utils import ThreadAdapter
from document_loaders import CyDocumentLoader,CyDocumentLoaderType


class CySemanticDB:
    def __init__(self,env:CyLangEnv):
        self.__env=env

    def create_context(self,context:CyLangContext):
        CyLangContextDao(self.__env).insert(context)
     
    def get_context(self,name:str)->CyLangContext:
        return CyLangContextDao(self.__env).get_by_name(name)
       
    def get_context_by_id(self,context_id:int)->CyLangContext:
        return CyLangContextDao(self.__env).get_by_id(context_id)

    def delete_context(self,id:int):
        CyLangContextDao(self.__env).delete(id)

    def get_context_all(self)->list[CyLangContext]:
        return CyLangContextDao(self.__env).get_all()

    def get_embs_types(self)->list:
        return CyLangContextDao(self.__env).get_embs_types()
    
    def get_context_types(self)->list:
        return CyLangContextDao(self.__env).get_types()
    
    def get_source_types(self)->list:
        return CyLangSourceDao(self.__env).get_types()

    def add_source(self,source:CyLangSource):
        CyLangSourceDao(self.__env).insert(source)

    def get_source(self,context_id:int,name:str)->CyLangSource:
        return CyLangSourceDao(self.__env).get(context_id,name)

    def get_source_all(self,context_id:int)->list[CyLangSource]:
       return CyLangSourceDao(self.__env).get_all(context_id)

    def remove_source(self,context_id:int,name:str):
        return CyLangSourceDao(self.__env).delete(context_id,name)
    
    def get_source_types(self)->list:
        return CyLangSourceDao(self.__env).get_types()
    
    def add_history(self,history:CyLangHistory):
        CyLangHistoryDao(self.__env).insert(history)

    def get_history(self, context_id:int,session_id:str,size:int)->list[CyLangHistory]:
        return CyLangHistoryDao(self.__env).get_history(context_id=context_id,session_id=session_id,size=size)  
    
    def clean_history(self):
        thr = ThreadAdapter(target=exec_clean_history, args=(self.__env,))
        thr.start()
 
    def add_llm(self,llm:CyLangLLMData):
        CyLangLLMDao(self.__env).insert(llm)

    def get_llm(self,context_id:int,name:str)->CyLangLLMData:
        return CyLangLLMDao(self.__env).get(context_id,name)

    def get_llm_all(self,context_id:int)->list[CyLangLLMData]:
       return CyLangLLMDao(self.__env).get_all(context_id)

    def remove_llm(self,context_id:int,name:str):
        return CyLangLLMDao(self.__env).delete(context_id,name)
    
    def get_llm_types(self)->list:
        return CyLangLLMDao(self.__env).get_types()

    def add_load(self, context_id:int, load_type:CyDocumentLoaderType,name:
                  str,content:str,path:str='',wait:bool=True,replace_rules:list=None):
        
        logging.info("Start add_load")

        context=CyLangContextDao(self.__env).get_by_id(context_id)
        if context is None:
            raise Exception("Context "+str(context_id)+" not found")

        model=CyEmbeddingsModel(context.embeddings_model_id)
        embs_config=None
        if model==CyEmbeddingsModel.HUGGING_FACE:
            embs_config=self.__env.get_config().get_embeddings_config()['hugging_face_embs']
        embs=CyEmbeddings(model=model,config=embs_config).embed_query(content)
        logging.info("len embeddings load content:%s",len(embs))

        embTableFieldSize=self.__env.get_config().get_embeddings_config()['tableFieldSize']
        embs=_pad0(embs,embTableFieldSize)
        
        logging.info("len embeddings load content (padded):%s",len(embs))
        load=CyLangLoad(name=name,context_id=context.id,content=content,embeddings=embs,
                         load_type_id=load_type.value,path=path)
        #logging.info("load values:%s",load.get_values())
        loadDao=CyLangLoadDao(self.__env)
        loadDao.insert(load)
        load=loadDao.get_by_name(name)

        loadDao.add_trace(load.id,"Load content embeddings OK")

        thread_load_chunks = ThreadAdapter(target=exec_load_chunks, args=(self.__env,context,load,replace_rules))
        thread_load_chunks.start()  
        if wait:
              thread_load_chunks.join()

        logging.info("End add_load")

    def get_load(self,name:str)->CyLangLoad:
        return CyLangLoadDao(self.__env).get_by_name(name)
 
    def get_load_by_id(self,id:int)->CyLangLoad:
        return CyLangLoadDao(self.__env).get_by_id(id)

    def remove_load(self,load_id:int):
        return CyLangLoadDao(self.__env).delete(load_id)

    def get_load_all(self,context_id:int)->list[CyLangLoad]:
        return CyLangLoadDao(self.__env).get_all(context_id)
    
    def get_load_types(self)->list:
        return CyLangLoadDao(self.__env).get_types()
 
    
    def similarity_search(self,context:CyLangContext,query:str)->list[CyLangChunk]:
        ret=[]
        
        embs_config=None
        if context.embeddings_model_id==CyEmbeddingsModel.HUGGING_FACE.value:
            embs_config=self.__env.get_config().get_embeddings_config()['hugging_face_embs']
       
        embs=CyEmbeddings(model=CyEmbeddingsModel(context.embeddings_model_id),config=embs_config).embed_query(query)
        embs_padded=_pad0(embs,self.__env.get_config().get_embeddings_config()['tableFieldSize'])


        #query @ chunks (20240207 modificato load_id in id nella query su cy_load)
        sql1=f"""select id,load_id,content,metadata,1-(embedding <=> '{embs_padded}') as similarity 
            from cy_chunk 
            where load_id in (select id from cy_load where context_id={context.id})
            and 1-(embedding <=> '{embs_padded}')>{context.chunk_threshold}
            order by similarity desc
            """
        
        thr1 = ThreadAdapter(target=exec_chunk_similarity, args=(self.__env,sql1))
        thr1.start()
        
        
        #query @ loads
        sql2=f"""select id,1-(embedding <=> '{embs_padded}') as similarity 
            from cy_load 
            where context_id={context.id}
            and 1-(embedding <=> '{embs_padded}')>{context.load_threshold}
            order by similarity desc
            """
        
        thr2 = ThreadAdapter(target=exec_load_similarity, args=(self.__env,sql2))
        thr2.start()
        
        # join
        ret1=thr1.join()  
        ret2=thr2.join()   
        
        for chunk in ret1:
            for load in ret2:
                if chunk.load_id==load.id:
                    chunk.similarity=chunk.similarity*context.chunk_weight+load.similarity*context.load_weight
                    break

        sorted_list = sorted(ret1, key=lambda x: x.similarity,reverse=True)            
        return sorted_list[:context.context_size]   
    
    def execute_sql_query(self,query) -> list:
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        res=dbConn.execute_select_query(query)
        dbConn.disconnect()
        return res


def exec_clean_history(env):
    CyLangHistoryDao(env).clean_history()

def exec_chunk_similarity(env,sql):
    ret=[]
    
    dbConn=env.get_semantic_db_connector()
    dbConn.connect()
    cur=dbConn.execute_query(sql,log_query=False)
    rows=cur.fetchall()
    for row in rows:
        chunk=CyLangChunk(row[2],row[3],similarity=row[4],id=row[0],load_id=row[1])
        ret.append(chunk)
    dbConn.disconnect()
    return ret

def exec_load_similarity(env,sql):
    ret=[]
    dbConn=env.get_semantic_db_connector()
    dbConn.connect()
    cur=dbConn.execute_query(sql,log_query=False)
    rows=cur.fetchall()
    for row in rows:
        load=CyLangLoad(id=row[0],similarity=row[1])
        ret.append(load)
    dbConn.disconnect()
    return ret

def exec_load_chunks(env:CyLangEnv,context:CyLangContext,load:CyLangLoad,
                     replace_rules:list):
    
    loadDao=CyLangLoadDao(env)
    try:
        loadDao.add_trace(load.id,"Starting loading documents")

        # print("load_type="+str(load.load_type))
        # print("load_path="+str(load.path))

        loader=CyDocumentLoader(CyDocumentLoaderType(load.load_type_id),load.path)
        docs=loader.load()

        loadDao.add_trace(load.id,"Loading documents OK")
        loadDao.add_trace(load.id,"Starting text splittering")

        embTableFieldSize=env.get_config().get_embeddings_config()['tableFieldSize']
        chunks=CyTextSplitter(chunk_size=context.chunk_size, chunk_overlap=context.chunk_overlap).split_documents(docs)
        logging.info('N.ro splitted documents:%s',len(chunks))
        model=CyEmbeddingsModel(context.embeddings_model_id)
        
        chunk_contents=[]
        for chunk in chunks:
            chunk_contents.append(chunk.page_content)
        logging.info('N.ro chunk contents:%s',len(chunk_contents))

        loadDao.add_trace(load.id,"Text splittering OK")
        loadDao.add_trace(load.id,"Starting replacing")

        if (replace_rules is not None):
                logging.info("replacing...")
                for chunk in chunk_contents:
                    for r in replace_rules:
                        chunk=chunk.replace(r[0],r[1])

        loadDao.add_trace(load.id,"End replacing")
        loadDao.add_trace(load.id,"Starting chunks embeddings")
       
        embs_config=None
        if model==CyEmbeddingsModel.HUGGING_FACE:
            embs_config=env.get_config().get_embeddings_config()['hugging_face_embs']
        
        batch_embs=CyEmbeddingsBatch(model=model,config=embs_config).embed_documents(chunk_contents,
                requestsPerMinute=env.get_config().get_embeddings_config()['requestsPerMinute'],
                callperBatch=env.get_config().get_embeddings_config()['callperBatch'])

        chunk_embs=[]
        for i in range(len(batch_embs)):
            e=_pad0(batch_embs[i],embTableFieldSize)
            chunk_embs.append(CyLangChunk(chunks[i].page_content,chunks[i].metadata,e))

        loadDao.add_trace(load.id,"Load chunks embeddings OK")
        
        CyLangChunkDao(env).insertChunks(CyLangChunks(load.id,chunk_embs)) 
        loadDao.add_trace(load.id,"Load chunks embeddings OK")
        loadDao.update_status(load.id,"OK")

    except (Exception) as error:
        logging.error(traceback.format_exc())
        loadDao.update_status(load.id,"Error")
    
   

def _pad0(a_in:list[float],size:int)->list[float]:
        ret=a_in
        for i in range(size-len(a_in)):
            ret.append(0)
        return ret    