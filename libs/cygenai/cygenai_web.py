import os
import logging,logging.handlers


from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cygenai_env import CyLangEnv

g_data={}

def startup():
    
    config_file=os.environ.get('CYGENAI_CONFIG_PATH')
    if config_file is None:
        config_file=os.environ.get('HOME','.')+'/sparklelang.json'
    
    if os.path.exists(config_file):    
        env=CyLangEnv(configFile=config_file)  
        g_data['env']=env
        logging.info("startup...")
    else:
        logging.error('%s not exists. Please configure environment variable CYGENAI_CONFIG_PATH',config_file)    

def shutdown():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # do startup
    startup() 
    app.mount(g_data['env'].get_config().get_web_server_config()['mount'], 
          StaticFiles(directory=g_data['env'].get_config().get_web_server_config()['root_folder'],html=True))
    
    yield
    # do shutdown

app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount(g_data['env'].get_config().get_web_server_config()['mount'], 
#           StaticFiles(directory=g_data['env'].get_config().get_web_server_config()['root_folder'],html=True))