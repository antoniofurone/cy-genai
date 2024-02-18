from langchain.text_splitter import RecursiveCharacterTextSplitter

class CyTextSplitter(RecursiveCharacterTextSplitter):
    chunck_size:int
    chunk_overlap:int

