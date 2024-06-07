from abc import ABC, abstractmethod
import logging,logging.handlers
from cygenai_utils import ThreadAdapter
import json

class CyLangAgent(ABC):
    def __init__(self,agent_name:str,config:dict=None,in_memory:bool=False):
        self.agent_name=agent_name
        self._config=config 
        self.result:dict=None
        self.next_agents:list[CyLangAgent]=list()
        self.in_memory=in_memory
        self.setup(config)

    def __eq__(self, other):
         if not isinstance(other, CyLangAgent):
            return NotImplemented
         return self.agent_name == other.agent_name  
    
    @abstractmethod
    def setup(self):
        # define here your agent
        pass

    @abstractmethod    
    def invoke(self,param:dict=None,prev_result:dict=None):
        pass    

    @abstractmethod
    def invoke_pre(self,param:dict)->dict:
        pass

    @abstractmethod
    def invoke_post(self,result:dict)->dict:
        pass
     
class CyLangSubDAG(ABC):
    
    def __init__(self,start_agent:CyLangAgent):
        self._start_agent=start_agent
        self.next_sub:CyLangSubDAG=None
        self.result:list[dict]=list()
   
    def invoke(self,param:dict=None,prev_result:dict=None)->dict:
        logging.info("SpkLangSubDAG:invoke:Start")   
        self.result:list[dict]=list() 
       
        if not self._start_agent:
            raise Exception("start agent non setted")
        
        thread_invoke_agent = ThreadAdapter(target=invoke_agent, args=(self._start_agent,self,param,prev_result))
        thread_invoke_agent.start()  
        thread_invoke_agent.join()

        logging.info("SpkLangSubDAG:invoke:End") 
        return self.result


def invoke_agent(agent:CyLangAgent,sub:CyLangSubDAG,param:dict,prev_result:dict):
    
    if not agent.in_memory or not agent.result:
        new_param=agent.invoke_pre(param=param)
        agent.invoke(param=new_param,prev_result=prev_result)
        agent.result=agent.invoke_post(agent.result)
     
    
    if len(agent.next_agents)==0:
        sub.result.append({
            'agent':agent.agent_name,
            'result':agent.result
            })
    else:
        threads_invoked:list[ThreadAdapter]=list()
        
        for ag in agent.next_agents:
              thread_invoke_agent = ThreadAdapter(target=invoke_agent, args=(ag,sub,param,{
                                                'result':agent.result
                                                }))
              thread_invoke_agent.start()
              threads_invoked.append(thread_invoke_agent)
              
        for thr in threads_invoked:
            thr.join()
      
class CyLangDAG(ABC):
    def __init__(self,start_sub:CyLangSubDAG):
        self._start_sub=start_sub
        self.result:dict=None


    def invoke(self,param:dict=None)->dict:
        sub=self._start_sub
        prev_res=None
        while sub:
            sub.invoke(param=param,prev_result=prev_res)
            self.result=sub.result
            prev_res=sub.result
            sub=sub.next_sub
        return self.result
      