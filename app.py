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

# DOCUMENT LOADING
loader = PyPDFLoader("./sample.pdf")

# SPLITTING
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# EMBEDDING AND VECTOR STORE
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# LLM
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
