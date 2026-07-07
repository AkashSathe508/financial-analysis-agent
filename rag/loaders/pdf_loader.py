from langchain_community.document_loaders import PyPDFLoader


def load_financial_report(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents
