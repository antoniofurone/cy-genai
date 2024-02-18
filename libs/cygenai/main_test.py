import sys
import json
import time
import os
import logging,logging.handlers

from cygenai_env import CyLangEnv
from cygenai_semantic import CySemanticDB
from cygenai_semantic_data import CyLangContext,CyLangContextType,CyLangChunk,CyLangLLMData
from cygenai_llm import CyLangLLM,CyLangLLMType
from embeddings import CyEmbeddingsModel
from document_loaders import CyDocumentLoader,CyDocumentLoaderType
from text_splitter import CyTextSplitter


def test_llm_vertex(chunks:list[CyLangChunk],question:str)->None:
    from langchain.prompts import PromptTemplate
    from langchain_google_vertexai import VertexAI
    from langchain.chains import LLMChain
    
    #logging.info(context)

    context=[]
    for chunk in chunks:
        context.append(chunk.content)
    context='\n'.join(context)

    template = """Answer the question based on the context below. If the
    question cannot be answered using the information provided answer
    with "I don't know".

    Context: {context}

    Question: {question}

    Answer: """

    prompt=template = PromptTemplate(input_variables=["context","question"],template=template)
    llm = VertexAI(temperature=0.7,model_name="gemini-pro")
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    answer = llm_chain.invoke(
        {
            "context": context,
            "question": question
        }
    )
   
    #print(answer)
    
    print("answer->"+answer['text'])

def test_llm_openai(chunks:list[CyLangChunk],question:str)->None:
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain_openai import OpenAI
    from langchain.chains import LLMChain

    context=[]
    for chunk in chunks:
        context.append(chunk.content)
    context='\n'.join(context)    

    template = """Answer the question based on the context below. If the
    question cannot be answered using the information provided answer
    with "I don't know".

    Context: {context}

    Question: {question}

    Answer: """

    prompt=template = PromptTemplate(input_variables=["context","question"],template=template)

    llm = ChatOpenAI(temperature=0.7)
    #llm=OpenAI(temperature=0.7)
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    answer = llm_chain.invoke(
        {
            "context": context,
            "question": question
        }
    )

    
    #print(answer)
    print("answer->"+answer['text'])

def create_db(env:CyLangEnv):
    env.desctroy_semantic_db()
    env.create_semantic_db()

def create_contexts(semanticDB:CySemanticDB):
    context=CyLangContext("alphabet1",1500,0,CyEmbeddingsModel.OPENAI.value,CyLangContextType.CHAT_BOT.value)
    semanticDB.create_context(context)

    context=CyLangContext("alphabet2",1500,0,CyEmbeddingsModel.GOOGLE_VERTEX_AI.value,CyLangContextType.CHAT_BOT.value,
                           chunk_threshold=0.69,load_threshold=0.69)
    
    semanticDB.create_context(context)

def create_llms(semanticDB:CySemanticDB):
    
    context1=semanticDB.get_context("alphabet1")
    
    llm_d1=CyLangLLMData(context1.id,"default",CyLangLLMType.CHAT_OPEAI.value,temperature=0.7,
                         prompt_template="""Answer the question based on the context below. If the
question cannot be answered using the information provided answer
with "I don't know".

Context: {context}

Question: {question}

Answer: """
    )
    semanticDB.add_llm(llm_d1)

    llm_d2=CyLangLLMData(context1.id,"secondario",CyLangLLMType.OPENAI.value,model_name='gpt-3.5-turbo-instruct',temperature=0.7)
    semanticDB.add_llm(llm_d2)

    context2=semanticDB.get_context("alphabet2")

    llm_d3=CyLangLLMData(context2.id,"default",CyLangLLMType.VERTEXAI.value,model_name="gemini-pro",temperature=0.7)
    semanticDB.add_llm(llm_d3)

def load_documents(semanticDB:CySemanticDB,context:CyLangContext):
    path="https://abc.xyz/investor/static/pdf/20230203_alphabet_10K.pdf"
    semanticDB.add_load(context_id=context.id,load_type=CyDocumentLoaderType.PDF,
                        name="annual report"+str(context.id),content="alphabet annual report",path=path)

    
def load_morelli(semanticDB:CySemanticDB,context:CyLangContext):
    
    path="c:/Temp/salvatore_morelli.pdf"
    semanticDB.add_load(context_id=context.id,load_type=CyDocumentLoaderType.PDF,
                        name="salvatore morelli"+str(context.id),content="vita di salvatore morelli",path=path)
    
def try_llm(semanticDB:CySemanticDB,context:CyLangContext,llm:CyLangLLM,query:str):
    logging.info("<---> "+query+" <--->")
    chunks=semanticDB.similarity_search(context,query)
    logging.info("answer ----> "+llm.invoke(chunks,query)['text'])  


   

def main():
    
    print("---- main_test.py ---")
    
    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/cygenai.json'
    
    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
        logging.info("startup...")
    else:
        logging.error('%s not exists. Please configure environment variable CYGENAI_CONFIG_PATH',config_file) 
        sys.exit() 

     

    create_db(env)
    semanticDB=CySemanticDB(env)    

    create_contexts(semanticDB)

    create_llms(semanticDB)

    context1=semanticDB.get_context("alphabet1")
    load_documents(semanticDB,context1)

    context2=semanticDB.get_context("alphabet2")
    load_documents(semanticDB,context2)
    
    logging.info("-----Open AI----------------------->")
    llm_conf_default=semanticDB.get_llm(context1.id,"default")
    llm_default=CyLangLLM(CyLangLLMType(llm_conf_default.llm_type_id),temperature=llm_conf_default.temperature,
                             template=llm_conf_default.prompt_template)
    
    llm_conf_secondary=semanticDB.get_llm(context1.id,"secondario")
    llm_secondary=CyLangLLM(CyLangLLMType(llm_conf_secondary.llm_type_id),model_name=llm_conf_secondary.model_name,
                              temperature=llm_conf_secondary.temperature)

    try_llm(semanticDB,context1,llm_default,"What was Alphabet's net income in 2022?")
    try_llm(semanticDB,context1,llm_default,"How much office space reduction took place in 2023?")
    try_llm(semanticDB,context1,llm_secondary,"What's the power of AI?")
    try_llm(semanticDB,context1,llm_secondary,"Dove è nato Salvatore Morelli?")
    
    
    logging.info("-----Vertex AI---------------------->")
    llm_basic_v=CyLangLLM(CyLangLLMType.VERTEXAI)
    llm_conf_default_v=semanticDB.get_llm(context2.id,"default")
    llm_default_v=CyLangLLM(CyLangLLMType(llm_conf_default_v.llm_type_id),
                             model_name=llm_conf_default_v.model_name,temperature=llm_conf_default_v.temperature)
    
    from langchain_openai import ChatOpenAI
    llm_ocb=CyLangLLM(llm=ChatOpenAI())
    llm_ocb_ita=CyLangLLM(llm=ChatOpenAI(),template= """Answer the question based only on the following context:
# {context}

# Question: {question}

# Answer in the following language: italian
# """)


    load=semanticDB.get_load("salvatore morelli")
    if load is not None:
         semanticDB.remove_load(load.id)

    try_llm(semanticDB,context2,llm_basic_v,"What was Alphabet's net income in 2022?")
    try_llm(semanticDB,context2,llm_default_v,"What was Alphabet's net income in 2022?")
    try_llm(semanticDB,context2,llm_ocb,"What was Alphabet's net income in 2022?")

    try_llm(semanticDB,context2,llm_basic_v,"How much office space reduction took place in 2023?")
    try_llm(semanticDB,context2,llm_default_v,"How much office space reduction took place in 2023?")
    try_llm(semanticDB,context2,llm_ocb,"How much office space reduction took place in 2023?")
    
    try_llm(semanticDB,context2,llm_basic_v,"What's the power of AI?")
    try_llm(semanticDB,context2,llm_default_v,"What's the power of AI?")
    try_llm(semanticDB,context2,llm_ocb,"What's the power of AI?")
    
    try_llm(semanticDB,context2,llm_basic_v,"Dove è nato Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_default_v,"Dove è nato Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_ocb,"Dove è nato Salvatore Morelli ?")

    load_morelli(semanticDB,context2)

    try_llm(semanticDB,context2,llm_basic_v,"Dove è nato Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_default_v,"Dove è nato Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_ocb,"Dove è nato Salvatore Morelli ?")
    
    try_llm(semanticDB,context2,llm_basic_v,"Quali sono state le principali opere di Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_default_v,"Quali sono state le principali opere di Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_ocb,"Quali sono state le principali opere di Salvatore Morelli ?")
    try_llm(semanticDB,context2,llm_ocb_ita,"Quali sono state le principali opere di Salvatore Morelli ?")


    
    logging.info("--- end ---")
    

if __name__ == "__main__":
    main()   


