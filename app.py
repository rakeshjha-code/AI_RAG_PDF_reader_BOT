from dotenv import load_dotenv
load_dotenv()

# Will help load PDFs in memory
from langchain_community.document_loaders import PyPDFLoader
# Will split the Document in chunks 
from langchain_text_splitters import RecursiveCharacterTextSplitter
# openaiembeddings will create embeddings for chunks , chatopenai will help to chat and ask QnA
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# vector databse
from langchain_community.vectorstores import InMemoryVectorStore
# Streamlit
import streamlit as st
from time import sleep
import os

#LLM
llm=ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

if "vector_db" not in st.session_state:
    st.session_state.vector_db=None

if  "messages"  not in st.session_state:
    st.session_state.messages=[]

def document_process(files):
    all_docs = []
    for file in files:
        temp_path = f"./uploaded_{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getvalue())
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        all_docs.extend(docs)
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # SPLITTING
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(all_docs)

    # EMBEDDING AND VECTOR STORE
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    vector_db = InMemoryVectorStore.from_documents(documents=split_docs, embedding=embeddings)

    st.session_state.vector_db = vector_db
    st.session_state.document_uploaded = True


st.subheader("DOCUMENT QnA ChatBot (RAG) - Ask Anything")

with st.sidebar:
    st.header("Controls")
    if st.button("Upload New Documents / Reset"):
        st.session_state.document_uploaded = False
        st.session_state.vector_db = None
        st.session_state.messages = []
        st.rerun()

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

# Document upload
if not st.session_state.document_uploaded:
    files = st.file_uploader(label="Select your PDF files", type="pdf", accept_multiple_files=True)
    if files:
        if st.button("Process Documents"):
            with st.spinner("Processing documents..."):
                document_process(files)
            st.success(f"{len(files)} document(s) uploaded successfully!")
            sleep(1.5)
            st.rerun()

if st.session_state.document_uploaded and st.session_state.vector_db:
    for oneMessage in st.session_state.messages:
        role=oneMessage["role"]
        content=oneMessage["content"]

        st.chat_message(role).markdown(content)

    query=st.chat_input("Ask anything...")
    if query:

        st.session_state.messages.append({"role":"user","content":query})

        st.chat_message("user").markdown(query)           
        documents=st.session_state.vector_db.similarity_search(query)
        context=""

        for doc in documents:
            context += doc.page_content +"\n\n"

        prompt=f""" You are a helpful assistant and provide answer based on the provided context.context:{context} and question is:{query} """
        result=llm.invoke(prompt)

        if hasattr(result, "text") and result.text:
            response_text = result.text
        elif isinstance(result.content, list):
            response_text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in result.content)
        else:
            response_text = str(result.content)

        st.session_state.messages.append({"role":"ai","content":response_text})
        st.chat_message("ai").markdown(response_text)  
