from cygenai_env import CyLangEnv
from cygenai_semantic_data import CyLangContext,CyLangLoad,CyLangChunk,CyLangChunks,CyLangLLMData,CyLangSource,CyLangHistory,CyLangApp
import hashlib
import logging


class CyLangUserDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env

    def login(self,email:str,pwd:str)->int:
        
        hash_object = hashlib.sha256()
        hash_object.update(pwd.encode())
        hash_password = hash_object.hexdigest()
        
        sql="select id from public.cy_user where email='"+email+"' and pwd='"+hash_password+"'"

        ret=-1
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            ret=row[0]
        dbConn.disconnect()
       
        return ret    

class CyLangAppDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env

    def insert(self,app:CyLangApp):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(app)
        dbConn.disconnect()

    def update_key(self,app:CyLangApp):
        cmd="update public.cy_app set app_key='"+app.app_key+"' where name='"+app.name+"'"
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command(cmd)
        dbConn.disconnect()

    def get_all(self)->list[CyLangApp]:
        ret=[]
        
        sql="select name,app_key,owner from public.cy_app"
          
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            app=CyLangApp(row[0],row[1],row[2])
            ret.append(app)
        dbConn.disconnect()
        return ret
    
    def get_by_name(self,name:str)->CyLangApp:
        sql="select name,app_key,owner from public.cy_app where name='"+name+"'"
      
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            context=CyLangApp(name=row[0],app_key=row[1],owner=row[2])
        else:
            context=None    
        dbConn.disconnect()    
        return context

    def delete(self,name:str):
        cmds=["delete from public.cy_app where name='"+name+"'"]

        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()    

class CyLangContextDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env

    def insert(self,context:CyLangContext):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(context)
        dbConn.disconnect()

    def get_by_name(self,name:str)->CyLangContext:
        sql="select a.id,a.context_name,a.chunk_size,a.chunk_overlap,a.embedding_model,"\
            +"a.context_type,a.context_size,a.chunk_threshold,a.load_threshold,a.chunk_weight,"\
            +"a.load_weight,a.history,b.name as embs_type_name,c.name as context_type_name "\
            +"from public.cy_context a "\
            +"join public.cy_embs_types b on b.id=a.embedding_model "\
            +"join public.cy_context_types c on c.id=a.context_type "\
            +"where a.context_name='"+name+"'"
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            context=CyLangContext(row[1],row[2],row[3],row[4],row[5],id=row[0],context_size=row[6],
                                   chunk_threshold=row[7],load_threshold=row[8],chunk_weight=row[9],
                                   load_weight=row[10],history=row[11],
                                   embeddings_model_name=row[12],context_type_name=row[13])
        else:
            context=None    
        dbConn.disconnect()    
        return context
    
    def get_by_id(self,context_id:int)->CyLangContext:
        sql="select a.id,a.context_name,a.chunk_size,a.chunk_overlap,a.embedding_model,"\
            +"a.context_type,a.context_size,a.chunk_threshold,a.load_threshold,a.chunk_weight,"\
            +"a.load_weight,a.history,b.name as embs_type_name,c.name as context_type_name "\
            +"from public.cy_context a "\
            +"join public.cy_embs_types b on b.id=a.embedding_model "\
            +"join public.cy_context_types c on c.id=a.context_type "\
            +"where a.id="+str(context_id)
        
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            context=CyLangContext(row[1],row[2],row[3],row[4],row[5],id=row[0],context_size=row[6],
                                   chunk_threshold=row[7],load_threshold=row[8],chunk_weight=row[9],load_weight=row[10],
                                   history=row[11],embeddings_model_name=row[12],context_type_name=row[13])
        else:
            context=None    
        dbConn.disconnect()
        return context

    def delete(self,id:int):
        cmds=["delete from public.cy_load_trace where load_id in (select load_id from public.cy_load where context_id="+str(id)+")"]
        cmds.append("delete from public.cy_chunk where load_id in (select id from public.cy_load where context_id="+str(id)+")")
        cmds.append("delete from public.cy_llm where context_id="+str(id))  
        cmds.append("delete from public.cy_history where context_id="+str(id))     
        cmds.append("delete from public.cy_source where context_id="+str(id))      
        cmds.append("delete from public.cy_load where context_id="+str(id))      
        cmds.append("delete from public.cy_context where id="+str(id))
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()

    def get_all(self)->list[CyLangContext]:
        ret=[]
        
        sql="select a.id,a.context_name,a.chunk_size,a.chunk_overlap,a.embedding_model,"\
            +"a.context_type,a.context_size,a.chunk_threshold,a.load_threshold,a.chunk_weight,"\
            +"a.load_weight,a.history,b.name as embs_type_name,c.name as context_type_name "\
            +"from public.cy_context a "\
            +"join public.cy_embs_types b on b.id=a.embedding_model "\
            +"join public.cy_context_types c on c.id=a.context_type"
          
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            context=CyLangContext(row[1],row[2],row[3],row[4],row[5],id=row[0],context_size=row[6],
                                   chunk_threshold=row[7],load_threshold=row[8],chunk_weight=row[9],
                                   load_weight=row[10],history=row[11],
                                   embeddings_model_name=row[12],context_type_name=row[13])
            ret.append(context)
        dbConn.disconnect()
        return ret
    
    def get_embs_types(self)->list:
        ret=[]
        sql="""select id,name from cy_embs_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret

    def get_types(self)->list:
        ret=[]
        sql="""select id,name from cy_context_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret


class CyLangHistoryDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env 

    def insert(self,history:CyLangHistory):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(history)
        dbConn.disconnect()

    def get_history(self,context_id:int,session_id:str,size:int)->list[CyLangHistory]:
        ret=[]

        sql="select query,answer from cy_history where context_id="+str(context_id)\
            +" and session_id='"+session_id+"' order by time_stamp desc limit "+str(size)   

        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            hist=CyLangHistory(context_id=context_id,session_id=session_id,query=row[0],answer=row[1])
            ret.append(hist)
        dbConn.disconnect()
        return ret


    def clean_history(self):
        history_timeout=self.__env.get_config().get_history_config()['time_out']
        cmd="delete from cy_history where session_id in (select session_id from ("\
            +"select session_id,EXTRACT(EPOCH from(CURRENT_TIMESTAMP-max(time_stamp))) as diff_sec from cy_history group by session_id"\
            +") as x where diff_sec>"+str(history_timeout)+")"
       
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command(cmd)
        dbConn.disconnect()
    

class CyLangSourceDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env 

    def insert(self,source:CyLangSource):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(source)
        dbConn.disconnect()

    def get(self,context_id:int,name:str):
        
        sql="select a.context_id,a.name,a.type_id,a.userid,a.pwd,a.host,a.port,a.service_name,a.database,b.name as source_type_name "\
            "from public.cy_source a "\
            "join public.cy_source_types b on a.type_id=b.id "\
            "where a.name='"+name+"' and a.context_id="+str(context_id)
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            source=CyLangSource(context_id=row[0],name=row[1],source_type_id=row[2],user_id=row[3],password=row[4],host=row[5],
                                 port=row[6],service_name=row[7],data_base=row[8],source_type_name=row[9])
        else:
            source=None    
        dbConn.disconnect()
        return source
    
    def get_all(self,context_id:int)->list[CyLangSource]:
        ret=[]
        
        sql="select a.context_id,a.name,a.type_id,a.userid,a.pwd,a.host,a.port,a.service_name,a.database,b.name as source_type_name "\
            "from public.cy_source a "\
            "join public.cy_source_types b on a.type_id=b.id "\
            "where a.context_id="+str(context_id)
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            source=CyLangSource(context_id=row[0],name=row[1],source_type_id=row[2],user_id=row[3],password=row[4],host=row[5],
                                 port=row[6],service_name=row[7],data_base=row[8],source_type_name=row[9])
            ret.append(source)
        dbConn.disconnect()
        return ret
    
    def delete(self,context_id:int,name:str):
        cmds=[("delete from public.cy_source where context_id="+str(context_id)+" and name='"+name+"'")]
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()

    def get_types(self)->list:
        ret=[]
        sql="""select id,name from public.cy_source_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret
    
class CyLangLLMDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env 

    def insert(self,llm:CyLangLLMData):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(llm)
        dbConn.disconnect()

    def get(self,context_id:int,name:str):
        
        sql="select a.context_id,a.name,a.llm_type,a.model_name,a.temperature,a.template,a.model_args,a.task,a.local,a.pt_pipeline,b.name as llm_type_name "\
            "from public.cy_llm a "\
            "join public.cy_llm_types b on a.llm_type=b.id "\
            "where a.name='"+name+"' and a.context_id="+str(context_id)
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            llm=CyLangLLMData(row[0],row[1],row[2],model_name=row[3],temperature=row[4],
                               prompt_template=row[5],model_args=row[6],task=row[7],local=row[8],pt_pipeline=row[9],llm_type_name=row[10])
        else:
            llm=None    
        dbConn.disconnect()
        return llm
    
    def get_all(self,context_id:int)->list[CyLangLLMData]:
        ret=[]
        
        sql="select a.context_id,a.name,a.llm_type,a.model_name,a.temperature,a.template,a.model_args,a.task,a.local,a.pt_pipeline,b.name as llm_type_name "\
            "from public.cy_llm a "\
            "join public.cy_llm_types b on a.llm_type=b.id "\
            "where a.context_id="+str(context_id)
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            llm=CyLangLLMData(row[0],row[1],row[2],model_name=row[3],temperature=row[4],
                               prompt_template=row[5],model_args=row[6],task=row[7],local=row[8],pt_pipeline=row[9],llm_type_name=row[10])
            ret.append(llm)
        dbConn.disconnect()
        return ret
    
    def delete(self,context_id:int,name:str):
        cmds=[("delete from public.cy_llm where context_id="+str(context_id)+" and name='"+name+"'")]
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()

    def get_types(self)->list:
        ret=[]
        sql="""select id,name from cy_llm_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret



class CyLangLoadDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env     

    def insert(self,load:CyLangLoad):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(load)
        dbConn.disconnect()

    def get_by_name(self,name:str)->CyLangLoad:
        sql="select a.id,a.load_name,a.context_id,a.content,a.status,a.path,a.load_type,b.name as load_type_name "\
            "from public.cy_load a "\
            "join public.cy_load_types b on a.load_type=b.id "\
            "where a.load_name='"+name+"'"
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            load=CyLangLoad(row[1],row[2],row[3],status=row[4],path=row[5],load_type_id=row[6],id=row[0],load_type_name=row[7])
        else:
            load=None    
        dbConn.disconnect()
        return load
    
    def get_by_id(self,id:int)->CyLangLoad:
        sql="select a.id,a.load_name,a.context_id,a.content,a.status,a.path,a.load_type,b.name as load_type_name "\
            "from public.cy_load a "\
            "join public.cy_load_types b on a.load_type=b.id "\
            "where a.id="+str(id)

        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        row=cur.fetchone()
        if row is not None:
            load=CyLangLoad(row[1],row[2],row[3],status=row[4],path=row[5],load_type_id=row[6],id=row[0],load_type_name=row[7])
        else:
            load=None    
        dbConn.disconnect()
        return load
    
    def delete(self,load_id:int):
        cmds=["delete from public.cy_chunk where load_id="+str(load_id)]
        cmds.append("delete from public.cy_load_trace where id="+str(load_id))
        cmds.append("delete from public.cy_load where id="+str(load_id))      
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()

    def get_all(self,context_id:int)->list[CyLangLoad]:
        ret=[]
       
        sql="select a.id,a.load_name,a.context_id,a.content,a.status,a.path,a.load_type,b.name as load_type_name "\
            "from public.cy_load a "\
            "join public.cy_load_types b on a.load_type=b.id "\
            "where a.context_id="+str(context_id)
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            load=CyLangLoad(row[1],row[2],row[3],status=row[4],path=row[5],load_type_id=row[6],id=row[0],load_type_name=row[7])
            ret.append(load)
        dbConn.disconnect()
        return ret
    
    def add_trace(self,load_id:int,step:str)->list[CyLangLoad]:
       cmdTrace="insert into cy_load_trace(load_id,time_stamp,step) values ("+str(load_id)+",CURRENT_TIMESTAMP,'"+\
            step+"')"
       dbConn=self.__env.get_semantic_db_connector()
       dbConn.connect()
       dbConn.execute_command(cmdTrace)
       dbConn.disconnect()

    def update_status(self,load_id:int,status:str):
        cmdTrace="update cy_load set status='"+status+"' where id="+str(load_id)
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command(cmdTrace)
        dbConn.disconnect()

    def delete(self,load_id:int):
        cmds=["delete from public.cy_chunk where load_id="+str(load_id)]
        cmds.append("delete from public.cy_load_trace where load_id="+str(load_id))
        cmds.append("delete from public.cy_load where id="+str(load_id))      
        
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_commands(cmds)
        dbConn.disconnect()  

    def get_types(self)->list:
        ret=[]
        sql="""select id,name from cy_load_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret


class CyLangChunkDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env  

    def insertChunks(self,chunks:CyLangChunks):
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        dbConn.execute_command_values(chunks)
        dbConn.disconnect()

class CyLangSpeechRecognitionDao():
    def __init__(self,env:CyLangEnv):
        self.__env=env  

    def get_types(self)->list:
        ret=[]
        sql="""select id,name from cy_speech_recognizer_types"""
        dbConn=self.__env.get_semantic_db_connector()
        dbConn.connect()
        cur=dbConn.execute_query(sql)
        rows=cur.fetchall()
        for row in rows:
            ret.append({'id':row[0],'name':row[1]})
        dbConn.disconnect()
        return ret
