import time
import logging
from enum import Enum
from langchain_openai import OpenAIEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


class CyEmbeddingsModel(Enum):
    GOOGLE_VERTEX_AI=1
    OPENAI=2
    HUGGING_FACE=3

class CyEmbeddings: 

    def __init__(self,model,config:dict=None):
        self._model=model
       
        if self._model==CyEmbeddingsModel.GOOGLE_VERTEX_AI:
            self._impl=self.__get_GoogleVertexAiModel()
        elif self._model==CyEmbeddingsModel.OPENAI:
            self._impl=self.__get_OpenAiModel()
        elif self._model==CyEmbeddingsModel.HUGGING_FACE:
            self._impl=self.__get_HuggingFaceModel(conf=config)    
        else:
            raise ValueError(model)
        return    
    
    def __get_GoogleVertexAiModel(self):
        return VertexAIEmbeddings()
    
    def __get_OpenAiModel(self):
        return OpenAIEmbeddings()

    def __get_HuggingFaceModel(self,conf:dict):
        hf_embs = HuggingFaceEmbeddings(
            model_name=conf['model_name'],    
            model_kwargs=conf['model_kwargs'], 
            encode_kwargs=conf['encode_kwargs'] 
            )
        return hf_embs

    def embed_documents(self,documents):
        return self._impl.embed_documents(documents) 

    def embed_query(self,query):
        return self._impl.embed_query(query) 
    
    def get_model(self):
        return self._impl

class CyEmbeddingsBatch(CyEmbeddings):
    
    def embed_documents(self,documents,requestsPerMinute:int,callperBatch:int)->[]:
        limiter = self.__rateLimit(requestsPerMinute)
        results = []
        docs = list(documents)
        while docs:
            head, docs = (
                docs[: callperBatch],
                docs[callperBatch :],
            )
            
            emb_chunks = super().embed_documents(head)
            results.extend(emb_chunks)

            logging.info("chucks to elab:%s",len(docs))
        
        return results

    def __rateLimit(self,requestsPerMinute:int):
        period = 60 / requestsPerMinute
        logging.info("waiting...")
        while True:
            before = time.time()
            yield 
            after = time.time()
            elapsed = after - before
            sleep_time = max(0, period - elapsed)
            if sleep_time > 0:
                logging.info("...")
                time.sleep(sleep_time)    

