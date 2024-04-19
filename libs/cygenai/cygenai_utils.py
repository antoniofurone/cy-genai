import locale
import json
import locale
from threading import Thread


class ThreadAdapter(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return      
    

def xor(s1, s2):
    return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])

def clean_query(query:str)->str:
    query=query.replace(";", "").replace("```sql", "").replace("```", "")
    idx=query.lower().index("select")
    if idx!=-1:
        query=query[idx:]
    return query

def format_cursor(rows:list):
    locale.setlocale(locale.LC_ALL, '')
    formatted_res_sql = []
    for row in rows:
        formatted_row = []
        for value in row:
            if isinstance(value, float):
                formatted_row.append(locale.format_string("%.2f", value, grouping=True))
            else:
                formatted_row.append(value)
        formatted_res_sql.append(formatted_row)
    return  formatted_res_sql   

 
 #da lista python a JSON @GF
def lista_a_json(lista):
    headers = lista[0]
    data = lista[1:]
    result = []
 
    for row in data:
        result.append(dict(zip(headers, row)))
 
    return json.dumps(result, indent=4)
 

