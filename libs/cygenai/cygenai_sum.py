from enum import Enum
from langchain_core.documents import BaseDocumentTransformer, Document
from typing import Iterable

class CyLangSumType(Enum):
    CHAT_OPEAI=1
    VERTEXAI=2

class CyLangLSum:
    def __init__(self, sum_type:CyLangSumType=CyLangSumType.CHAT_OPEAI,llm=None,model_name:str=None, 
                 temperature:float=None,template:str=None
                ):
        pass

    def invoke(self,documents: Iterable[Document])->dict:
        pass