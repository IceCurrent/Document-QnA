# import chainlit as cl
# from chainlit.types import AskFileResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.document_loaders import TextLoader, PyPDFLoader, BSHTMLLoader, JSONLoader, UnstructuredMarkdownLoader
from langchain.document_loaders import GoogleDriveLoader
from langchain.document_loaders.csv_loader import CSVLoader
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials.json"

textSplitter = RecursiveCharacterTextSplitter(chunk_size= 1000)


# def Process_file(file):
#     import tempfile
#     Loader = None
#     if file.type == "text/plain":
#         Loader = TextLoader

#     elif file.type == "text/html":
#         Loader = BSHTMLLoader
    
#     elif file.type == "text/markdown":
#         Loader = UnstructuredMarkdownLoader
    
#     elif file.type == "text/csv":
#         Loader = CSVLoader

#     elif file.type == "application/pdf":
#         Loader = PyPDFLoader
    
#     elif file.type == "application/json":
#         Loader = JSONLoader
    
#     else:
#         print("Error: Invalid File Format")
#         exit(0)
    
#     with tempfile.NamedTemporaryFile() as tempfile:
#         tempfile.write(file.content)
#         loader = Loader(tempfile.name)
#         docs = loader.load()
        
#     chunkList = textSplitter.split_documents(documents=docs)
    
#     print("length of chunkList = ", len(chunkList))
#     #creating metadata for each chunk
#     for i, chunk in enumerate(chunkList):
#         chunk.metadata["source"] = f"source_{i}"
    
#     return chunkList
    

def Process_from_drive():
    loader = GoogleDriveLoader (
        folder_id="1gWROE64sh6oBhElABaKiblHQYN5pOYvZ",
        # folder_id="19_XvU3wloSa54WQCDHQlFH-d1z7T89q5",
        # document_ids=["10otMtsBCkaLWhufNRbFvyiGsFmBHUhhQJFotXmWSA0s"],
        credentials_path= "/app/credentials.json",
        token_path="/app/token.json",
        recursive=False,
    )

    docs = loader.load()
    chunkList = textSplitter.split_documents(documents=docs)

    print("length of chunkList = ", len(chunkList))

    #creating metadata for each chunk
    for i, chunk in enumerate(chunkList):
        chunk.metadata["source"] = f"source_{i}"
    
    return chunkList


print(Process_from_drive())