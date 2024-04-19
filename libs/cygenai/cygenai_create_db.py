import os
import logging
import sys

from cygenai_env import CyLangEnv 

def main():
    
    print("---- create db ---")

    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/cygenai.json'
    
    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
        logging.info("startup...")
    else:
        logging.error('%s not exists. Please configure environment variable CYGENAI_CONFIG_PATH',config_file) 
        sys.exit() 

    env.desctroy_semantic_db()
    
    env.create_semantic_db()    

    print("---- end create db ---")  

if __name__ == "__main__":
    main()   
