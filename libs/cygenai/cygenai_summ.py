from enum import Enum
from langchain_core.documents import Document
from typing import Iterable
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain_openai import ChatOpenAI
from langchain_google_vertexai import VertexAI
from langchain_openai import OpenAI

from cygenai_llm import CyLangLLMType



class CyLangLSumm:
    def __init__(self, llm_type:CyLangLLMType=CyLangLLMType.CHAT_OPEAI,llm=None,model_name:str=None, 
                 temperature:float=None,template:str=None
                ):
       
        if template is None:
            self.template=""""Write a concise summary of the following:
"{text}"
CONCISE SUMMARY:"""
        else:
            self.template=template

        if llm is None:
        
            self.llm_type=llm_type
            self.temperature=temperature
            self.model_name=model_name
            
            if self.llm_type==CyLangLLMType.CHAT_OPEAI:
                if self.model_name is not None:
                    self.llm=ChatOpenAI(model=model_name)
                else:
                    self.llm=ChatOpenAI()

            elif self.llm_type==CyLangLLMType.OPENAI:
                
                if self.model_name is not None:
                    self.llm=OpenAI(model=model_name)
                else:
                    self.llm=OpenAI()

            elif self.llm_type==CyLangLLMType.VERTEXAI:
                if self.model_name is not None:
                    self.llm=VertexAI(model_name=self.model_name)
                else:
                    self.llm=VertexAI()    
            else:
                raise ValueError(self.llm_type)  

            if self.temperature is not None:
                self.llm.temperature=self.temperature 
        else:
            self.llm=llm        

    def invoke(self,documents: Iterable[Document])->dict:
        
        prompt = PromptTemplate.from_template(self.template)
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")
        return stuff_chain.invoke(documents)