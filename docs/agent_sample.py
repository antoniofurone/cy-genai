from cygenai_agent import CyLangAgent,CyLangSubDAG,CyLangDAG
from cygenai_env import CyLangEnv
from document_loaders import CyDocumentLoader,CyDocumentLoaderType
from cygenai_llm import CyLangLLM,CyLangLLMType
from cygenai_semantic import CyLangChunk

import logging,logging.handlers
import sys
import os


class Wiki(CyLangAgent):
    def setup(self,config:dict=None):
            self.loader=CyDocumentLoader(type=CyDocumentLoaderType.WEB,
                                          path="https://en.wikipedia.org/wiki/Jannik_Sinner")
    
    def invoke(self,param:dict=None,prev_result:dict=None):
            logging.info("Invoke Agent:"+self.agent_name)
            docs=self.loader.load()
            self.result={}
            self.result['wiki_docs']=docs
        
    def invoke_pre(self,param:dict)->dict:
        return param

    def invoke_post(self,result:dict)->dict:
        return result
     
class LLM(CyLangAgent):
    def setup(self,config:dict=None):
            self.llm=CyLangLLM(config['llm_type'])
    
    def invoke(self,param:dict=None,prev_result:dict=None):
        logging.info("Invoke Agent:"+self.agent_name)
        docs=prev_result['result']['wiki_docs']
        chunks:list[CyLangChunk]=list()
        for d in docs:
             chunks.append(CyLangChunk(content=d.page_content[:15000],metadata={'source':'wiki agent'}))
        query=param['query']
        answer=self.llm.invoke(contexts=chunks,query=query)['text']
        self.result={'query': query,'answer':answer}  
        
    def invoke_pre(self,param:dict)->dict:
        return param

    def invoke_post(self,result:dict)->dict:
        return result   

class Printer(CyLangAgent):
      def setup(self,config:dict=None):
        pass
      def invoke(self,param:dict=None,prev_result:dict=None):
        logging.info("Invoke Agent:"+self.agent_name)
        
        print(param)
        print(prev_result)
        
        self.result=prev_result

      def invoke_pre(self,param:dict)->dict:
        return param
      def invoke_post(self,result:dict)->dict:
        return result   
      

class CyLangExtention:
    def execute(self,param:dict)->dict:
        
        wiki=Wiki("wiki",in_memory=True) 
        wiki.next_agents.append(LLM("OpenAI",config={'llm_type':CyLangLLMType.CHAT_OPEAI})) 
        wiki.next_agents.append(LLM("Vertex",config={'llm_type':CyLangLLMType.VERTEXAI})) 

        sub1=CyLangSubDAG(start_agent=wiki)
        printer=Printer('printer')
        sub1.next_sub=CyLangSubDAG(start_agent=printer)

        dag=CyLangDAG(start_sub=sub1)
        
        return dag.invoke({'query':'When was born Yannick Sinner ?'})
        

def main():

    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/cygenai.json'
    
    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
        logging.info("startup...")
    else:
        logging.error('%s not exists. Please configure environment variable SPKLANG_CONFIG_PATH',config_file) 
        sys.exit() 

    extention=CyLangExtention()
    extention.execute({})
    
if __name__ == "__main__":
    main()   
