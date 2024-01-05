from decouple import config
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import TextLoader, MergedDataLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma


OPENAI_API_KEY = config("OPENAI_API_KEY")


def _load_documents(transcript, summary, chapters):
    # Temporary save text to file
    with open("transcript.txt", "w") as f:
        f.write(transcript)
    with open("summary.txt", "w") as f:
        f.write(summary)
    with open("chapters.txt", "w") as f:
        f.write(chapters)
    # Create the loaders
    loader_transcript = TextLoader("transcript.txt")
    loader_summary = TextLoader("summary.txt")
    loader_chapters = TextLoader("chapters.txt")
    # Merge the loaders
    loader_all = MergedDataLoader(loaders=[loader_transcript, loader_summary, loader_chapters])
    # Load the documents
    documents = loader_all.load()
    return documents


def _split_documents(documents):
    splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
    texts = splitter.split_documents(documents)
    return texts


def _create_retriever(texts):
    db = Chroma.from_documents(texts, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))
    retriever = db.as_retriever()
    return retriever


def _process_data(transcript, summary, chapters):
    documents = _load_documents(transcript, summary, chapters)
    texts = _split_documents(documents)
    retriever = _create_retriever(texts)
    return retriever


def start_chat(transcript, summary, chapters):
    print("Starting chat...")
    retriever = _process_data(transcript, summary, chapters)
    memory = ConversationBufferMemory(memory_key="chat_history", input_key='question', output_key='answer',
                                      return_messages=True)
    model = ChatOpenAI(model="gpt-3.5-turbo-0613", openai_api_key=OPENAI_API_KEY, temperature=0)
    qa_chain = ConversationalRetrievalChain.from_llm(model, retriever=retriever,
                                                     return_source_documents=True, memory=memory)
    return qa_chain


def ask_question(question, qa_chain):
    result = qa_chain(question)
    return result
