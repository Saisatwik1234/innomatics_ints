import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# Replace with your actual Gemini API Key
os.environ["GOOGLE_API_KEY"] = "*****************************"

def ingest_pdf(file_path: str, persist_directory: str = "./chroma_db"):
    """
    Loads a PDF, chunks the text, and stores the embeddings in a local vector database.
    """
    print(f"📄 Loading document: '{file_path}'...")
    
    # 1. Load the PDF
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"✅ Successfully loaded PDF. Total pages: {len(documents)}")
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")
        return None

    # 2. Split the text into chunks
    # We use 1000 characters with a 200-character overlap to maintain context between chunks
    print("✂️  Splitting document into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks.")

    # 3. Create Embeddings and Store in ChromaDB
    print("🧠 Generating embeddings and saving to vector store (This might take a moment)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # This creates the database and saves it to the persist_directory (./chroma_db)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"🎉 Ingestion complete! Database saved to '{persist_directory}' folder.")
    return vectorstore

# ==========================================
# EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    # Specify the name of your PDF file here. 
    # Make sure the PDF is in the same folder as this script!
    pdf_filename = "support_document.pdf" 
    
    if os.path.exists(pdf_filename):
        ingest_pdf(pdf_filename)
    else:
        print(f"⚠️  File '{pdf_filename}' not found. Please place a PDF in the folder and update the filename.")
