import os
import logging
import sys
import uvicorn
from cygenai_env import CyLangEnv

class CyLangWebServer:
    
    def __init__(self,env:CyLangEnv):
        self.__env=env
    
    def start(self):
        logging.info("Start web server ...")
        api_config=self.__env.get_config().get_web_server_config()
        host=api_config['host']
        port=api_config['port']
        logging.info("api_host="+host)
        logging.info("api_port="+str(port))
        
        uvicorn.run("cygenai_web:app", host=host, port=port, log_level="info",reload=False,
                    ssl_keyfile=self.__env.get_config().get_security_config()['key_file'], ssl_certfile=self.__env.get_config().get_security_config()['cert_file'])
        logging.info("... api server stopped")


def main():
    
    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/cygenai.json'
    
    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
    else:
        logging.error('%s not exists. Please configure environment variable CYGENAI_CONFIG_PATH',config_file) 
        sys.exit()  
    
    CyLangWebServer(env).start()

if __name__ == "__main__":
    main()
