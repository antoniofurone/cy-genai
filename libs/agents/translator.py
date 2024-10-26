from cygenai_agent import CyLangAgent,CyLangSubDAG,CyLangDAG
from cygenai_env import CyLangEnv
from cygenai_llm import CyLangLLM,CyLangLLMType

import logging,logging.handlers
import os
import sys

class CyLangTranslator(CyLangAgent):
    def setup(self,config:dict=None):
        if 'llm_type' in config:
            llm_type=config['llm_type']
        else:
            llm_type=CyLangLLMType.VERTEXAI
        logging.info("llm_type="+str(llm_type))
        
        if 'prompt_template' in config:
            prompt_template=config['prompt_template']
        else:
            prompt_template='Translate the following sentece from italian to english: {question}'
        logging.info("prompt_template="+prompt_template)

        if 'model' in config:
            model_name=config['model']
        else:
            model_name='gemini-pro'
        logging.info("model_name="+model_name)
        
        if 'temperature' in config:
            temperature=config['temperature']
        else:
            temperature=0.1
        logging.info("temperature="+str(temperature))
        
        self.llm=CyLangLLM(llm_type=llm_type,template=prompt_template,
                            model_name=model_name,temperature=temperature)

    def invoke(self,param:dict=None,prev_result:dict=None):
        answer=self.llm.invoke(contexts=[],query=param['sentence'])['text']
        self.result={'query': param['sentence'],'answer':answer}  
        
    def invoke_pre(self,param:dict)->dict:
        return param

    def invoke_post(self,result:dict)->dict:
        return result      

class CyLangExtention:
    def execute(self,param:dict)->dict:
       
        in_memory=False
        if 'load_in_memory' in param:
            if param['load_in_memory']:
                in_memory=True
        
        logging.info("in_memory="+str(in_memory))    

        translator=CyLangTranslator("translator",config=param,in_memory=in_memory)
        sub1=CyLangSubDAG(start_agent=translator)
        dag=CyLangDAG(start_sub=sub1)
        return dag.invoke(param) 
     
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

    param={'llm_type':CyLangLLMType.CHAT_OPEAI,
           'temperature':0.2,
           'prompt_template':'Translate the following sentece from italian to english: {question}',
           'model':'gpt-4o-mini',
           'load_in_memory':True,
           'sentence':'oggi non so proprio cosa mangiare'}

    #param={'sentence':'oggi non so proprio cosa mangiare'}


    extention=CyLangExtention()
    print(extention.execute(param=param))

    param['sentence']='Domani potrà anche piovere'
    print(extention.execute(param=param))

if __name__ == "__main__":
    main()   