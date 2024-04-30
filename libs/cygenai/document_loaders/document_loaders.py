from enum import Enum
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.document_loaders import WebBaseLoader


class CyDocumentLoaderType(Enum):
    PDF=1
    FILE_DIRECTORY=2
    CSV=3
    UNSTRUCTURED_HTML=4
    BS_HTML=5
    WEB=6

class CyDocumentLoader:
    
    def __init__(self,type,path):
        if type==CyDocumentLoaderType.PDF:
            self.__impl=self.__get_PdfLoader(path)
        elif type==CyDocumentLoaderType.FILE_DIRECTORY:
            self.__impl=self.__get_FileDirLoader(path)
        elif type==CyDocumentLoaderType.CSV:
            self.__impl=self.__get_CsvLoader(path)
        elif type==CyDocumentLoaderType.UNSTRUCTURED_HTML:
            self.__impl=self.__get_UnHtmlLoader(path)  
        elif type==CyDocumentLoaderType.BS_HTML:
            self.__impl=self.__get_BsHtmlLoader(path)      
        elif type==CyDocumentLoaderType.WEB:
            self.__impl=self.__get_WebLoader(path)         
        else:
            raise ValueError(type)
        return    
    
    def __get_PdfLoader(self,path):   
        return PyPDFLoader(path)
    
    def __get_FileDirLoader(self,path):
        return DirectoryLoader(path)

    def __get_CsvLoader(self,path):
        return CSVLoader(path)

    def __get_UnHtmlLoader(self,path):
        return UnstructuredHTMLLoader(path)
    
    def __get_BsHtmlLoader(self,path):
        return BSHTMLLoader(path)
    
    def __get_WebLoader(self,path):
        return WebBaseLoader(path)

    def load(self):
        return self.__impl.load() 

    def embed_query(self,query):
        return self.__impl.embed_query(query) 
    
    def get_loader(self):
        return self.__impl
   