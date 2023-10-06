import chainlit as cl
from chainlit.types import AskFileResponse
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
# from langchain.document_loaders import TextLoader, PyPDFLoader, BSHTMLLoader, JSONLoader, UnstructuredMarkdownLoader
# from langchain.document_loaders.csv_loader import CSVLoader
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from processData import Process_from_drive
import os

os.environ["OPENAI_API_KEY"] = os.environ.get("API_KEY")

system_template = """Use the following pieces of context to answer the users question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.
The "SOURCES" part should be a reference to the source of the document from which you got your answer.

And if the user greets with greetings like Hi, hello, How are you, etc reply accordingly as well.

Example of your response should be:

The answer is foo
SOURCES: xyz


Begin!
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}


def getDocs():
    # chunkList = Process_file(file)
    chunkList = Process_from_drive()

    cl.user_session.set("docs", chunkList)

    embeddings = OpenAIEmbeddings()

    #creating a chroma db
    docs = Chroma.from_documents (
        chunkList, embeddings,
    )

    return docs


@cl.on_chat_start
async def processing():
    # files = None

    # getting file from user

    # while files == None:
    #     files = await cl.AskFileMessage(
    #         content="""Welcome to METAKGP!\n
    #         Ask almost anything regarding KGP!\n
    #         You can also begin by uploading a file.\n
    #         (Since this is a prototype application, therefore, we ask to upload a file.
    #         In the real application, this would be done in the back-end, such that
    #         our app has all the Metakgp data)
    #         """,
            
    #         accept=["text/plain", "application/pdf", "text/html", "text/markdown", "application/json", "text/csv"],
    #         max_size_mb=6,
    #         timeout=180
    #     ).send()
    
    # file = files[0]

    #cl.Message.send() is an asynchronous method, so always use await
    # msg =  cl.Message(
    #     content= f"Processing your file {file.name}...", 
    #     disable_human_feedback=True #Whenever a progress bar is loading we always disable human feedback
    # )

    # await msg.send()
    print("and so it starts")

    await cl.Message(content="""Welcome to METAKGP!\n
            Ask almost anything regarding KGP!\n
    """).send()

    # docs = getDocs()
    docs = await cl.make_async(getDocs)()

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0.77, streaming=True),
        chain_type="stuff",
        memory = memory,
        retriever = docs.as_retriever(max_tokens_limit = 4097),
    )

    # msg.content = f"{file.name} processed, you can now ask any questions!"
    # await msg.update()

    cl.user_session.set("chain", chain)
    await cl.Message(content="Processing Complete").send()



@cl.on_message
async def main(message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )

    cb.answer_reached = True
    res = await chain.acall(message, callbacks=[cb])

    answer = res["answer"]
    sources = res["sources"].strip()

    # print("type of sources = " ,  type(sources))
    print("sources = ", sources)
    # print ("sources = " + sources)
    source_elements = []

    docs = cl.user_session.get("docs")
    metadatas = [doc.metadata for doc in docs]
    all_sources = [m["source"] for m in metadatas]

    print("all_sources = ", all_sources)

    if sources:
        found_sources = []

        for src in sources.split(", "):
            #split->
    
            # print("type of src = " , type(src))
            print ("src = " + src)

            # s = src.split()
            # source_name = s[0].replace(".", "")

            # source_name = src
            # print ("source_name = " + source_name)

            try:
                index = all_sources.index(src)
                print("index = ", index)
            except ValueError:
                continue

            text = docs[index].page_content
            # print("text = ", text)
            found_sources.append(src)

            source_elements.append(cl.Text(content=text, name=src))
            # print("type of source elements entries = ", type(source_elements[0]))

        if found_sources:
            answer += f"\nSources: {', '.join(found_sources)}"
            # print("answer = ", answer)
        else:
            answer += "\nNo sources found"
            # print("answer = ", answer)

    
    if cb.has_streamed_final_answer:
        cb.final_stream.elements = source_elements
        await cb.final_stream.update()
    else:
        await cl.Message(content=answer, elements=source_elements).send()
    



# print(getDocs())




