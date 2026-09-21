import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent / "docs"
CHROMA_DIR = Path(__file__).parent / "chroma_db"


def _has_openai_key() -> bool:
    key = os.getenv("OPENAI_API_KEY", "")
    return bool(key) and not key.startswith("sk-your-key")


def _is_demo_mode() -> bool:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    return provider == "openai" and not _has_openai_key()

SYSTEM_PROMPT = """Tu es SmartDoc DSI, un assistant interne de la Direction des Systèmes d'Information.
Réponds uniquement à partir du contexte documentaire fourni.
Si la réponse n'est pas dans les documents, dis clairement que tu ne disposes pas de cette information.
Réponds en français, de manière concise et structurée.
Cite le nom du document source quand c'est pertinent.

Contexte :
{context}
"""


def _get_embeddings():
    if _is_demo_mode():
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings

        model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaEmbeddings(model=model, base_url=base_url)

    from langchain_openai import OpenAIEmbeddings

    model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model)


def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama

        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=0)

    from langchain_openai import ChatOpenAI

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)


def _load_documents():
    documents = []
    for pattern in ("**/*.md", "**/*.txt"):
        loader = DirectoryLoader(
            str(DOCS_DIR),
            glob=pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=False,
        )
        documents.extend(loader.load())
    return documents


def _build_vectorstore():
    documents = _load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(documents)

    embeddings = _get_embeddings()
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


def get_retriever():
    embeddings = _get_embeddings()

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
        )
    else:
        vectorstore = _build_vectorstore()

    return vectorstore.as_retriever(search_kwargs={"k": 4})


def _format_docs(docs):
    parts = []
    for doc in docs:
        source = Path(doc.metadata.get("source", "document")).name
        parts.append(f"[{source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_rag_chain():
    retriever = get_retriever()
    llm = _get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def _demo_answer(question: str, docs) -> str:
    if not docs:
        return (
            "Je n'ai trouvé aucune information pertinente dans la documentation DSI "
            f"pour : « {question} »."
        )

    intro = (
        "*(Mode démo — embeddings locaux, sans LLM. "
        "Ajoutez OPENAI_API_KEY dans .env pour des réponses générées.)*\n\n"
    )
    body = _format_docs(docs)
    sources = sorted({Path(d.metadata.get("source", "")).name for d in docs if d.metadata.get("source")})
    footer = f"\n\n**Sources :** {', '.join(sources)}"
    return intro + body + footer


def ask(question: str) -> str:
    if _is_demo_mode():
        retriever = get_retriever()
        docs = retriever.invoke(question)
        return _demo_answer(question, docs)

    chain = build_rag_chain()
    return chain.invoke(question)
