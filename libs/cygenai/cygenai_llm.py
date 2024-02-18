import json
from enum import Enum
import logging,logging.handlers

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_google_vertexai import VertexAI
from langchain.chains import LLMChain
from langchain_community.llms import HuggingFaceHub

from cygenai_semantic_data import CyLangChunk

class CyLangLLMType(Enum):
    CHAT_OPEAI=1
    OPENAI=2
    VERTEXAI=3
    HUGGING_FACE=4

class CyLangLLM:
    def __init__(self, llm_type:CyLangLLMType=CyLangLLMType.CHAT_OPEAI,llm=None,model_name:str=None, 
                 temperature:float=None,template:str=None,model_args:str=None,task:str=None,
                 local:bool=False,pt_pipeline:bool=False
                ):
        if template is None:
            self.template="""Answer the question based on the context below. If the
question cannot be answered using the information provided answer
with "I don't know".

Context: {context}

Question: {question}

Answer: """
        else:
            self.template=template    

        if llm is None:
        
            self.llm_type=llm_type
            self.temperature=temperature
            self.model_name=model_name
            self.model_args=model_args
            self.task=task
            self.local=local
            self.pt_pipeline=pt_pipeline
            
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

            elif self.llm_type==CyLangLLMType.HUGGING_FACE:
                
                if self.model_name is None:
                    raise ValueError("For HUGGING FACE model_name (repo_id) is required")

                model_kwargs={}    
                if self.temperature is not None:
                    model_kwargs['temperature']=self.temperature
                
                if self.model_args is not None:
                    args = json.loads(self.model_args)
                    model_kwargs.update(args)

                logging.info("model_kwargs for HUGGING FACE model:"+json.dumps(model_kwargs))

                if local:
                    if task is None:
                        raise ValueError("For local model, task is required")
                    
                    if pt_pipeline:
                        self.__build_pipeline(model_kwargs)      
                    else:

                        from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

                        self.llm = HuggingFacePipeline.from_model_id(
                            model_id=self.model_name,
                            task=self.task,
                            pipeline_kwargs=model_kwargs,
                        )
 
                else:    
                    self.llm = HuggingFaceHub(repo_id=model_name, model_kwargs=model_kwargs)

            else:
                raise ValueError(self.llm_type)        

            if self.temperature is not None and self.llm_type!=CyLangLLMType.HUGGING_FACE:
                    self.llm.temperature=self.temperature    
        else:
            self.llm=llm 
            self.pt_pipeline=False   

    def invoke(self,coontexts:list[CyLangChunk], query:str, addition:str=None)->dict:
        
        if not coontexts:
            logging.warning("Array of chunks for context is empty")
        else:
            logging.info("Array of chunks for context has length:"+str(len(coontexts)))

        context=[]
        for ctx in coontexts:
            context.append(ctx.content)

        context='\n'.join(context) 

        if addition is not None:    
            self.template = self.template + addition


        if (self.pt_pipeline):
            return self.__invoke_pipeline(context=context,query=query)           
        else:
            return self.__invoke_chain(context=context,query=query)
    
    def __build_pipeline(self,model_kwargs:dict):
        from transformers import pipeline                    

        self.pipeline = pipeline(
            task=self.task, 
            model=self.model_name, 
            model_kwargs=model_kwargs
            )

        
    
    def __invoke_chain(self,context:str,query:str):
        
        prompt = PromptTemplate(input_variables=["context","question"],template=self.template)
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)

        logging.debug("-------------------- __invoke_chain: INIZIO LOGGING PARAMETRI LLM ---------------------")
        logging.debug("template="+self.template)
        logging.debug("context="+context)
        logging.debug("question="+query)
        logging.debug("-------------------- __invoke_chain: FINE LOGGING PARAMETRI LLM -----------------------")

        return llm_chain.invoke(
        {
            "context": context,
            "question": query
        })     

    def __invoke_pipeline(self,context:str,query:str):
       
        logging.debug("-------------------- __invoke_pipeline: INIZIO LOGGING PARAMETRI LLM ---------------------")
        logging.debug("context="+context)
        logging.debug("question="+query)
        logging.debug("task="+self.task)
        logging.debug("-------------------- __invoke_pipeline: FINE LOGGING PARAMETRI LLM -----------------------")

        if self.task=='question-answering' and (context is None or context==''):
            return None
        
        if self.task=='question-answering':
            answer = self.pipeline(
                    question=query,
                    context=context,
            )
        elif self.task=='text-classification':
            answer = self.pipeline(query)  
        elif self.task=='sentiment-analysis':
            answer = self.pipeline(query)       
        elif self.task=='text-generation':
            answer = self.pipeline(query)
        elif self.task=='text2text-generation':
            answer = self.pipeline(query)    
        else:
            raise ValueError("Task ["+self.task+"] not supported via pt pipeline")

        return answer 

   
