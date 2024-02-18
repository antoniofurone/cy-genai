from enum import Enum
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader

class CyDocumentLoaderType(Enum):
    PDF=1
    FILE_DIRECTORY=2
    CSV=3
    HTML=4

class CyDocumentLoader:
    
    def __init__(self,type,path):
        if type==CyDocumentLoaderType.PDF:
            self.__impl=self.__get_PdfLoader(path)
        elif type==CyDocumentLoaderType.FILE_DIRECTORY:
            self.__impl=self.__get_FileDirLoader(path)
        elif type==CyDocumentLoaderType.CSV:
            self.__impl=self.__get_CsvLoader(path)
        elif type==CyDocumentLoaderType.HTML:
            self.__impl=self.__get_HtmlLoader(path)    
        else:
            raise ValueError(type)
        return    
    
    def __get_PdfLoader(self,path):   
        return PyPDFLoader(path)
    
    def __get_FileDirLoader(self,path):
        return DirectoryLoader(path)

    def __get_CsvLoader(self,path):
        return CSVLoader(path)

    def __get_HtmlLoader(self,path):
        return UnstructuredHTMLLoader(path)
    
    def load(self):
        return self.__impl.load() 

    def embed_query(self,query):
        return self.__impl.embed_query(query) 
    
    def get_loader(self):
        return self.__impl
   