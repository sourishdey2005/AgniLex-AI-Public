import os
import pickle
import json
from typing import List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize embedding model (lightweight)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBEDDING_MODEL)

# Vector store path
VECTORSTORE_PATH = "./vectorstore"
os.makedirs(VECTORSTORE_PATH, exist_ok=True)


class RAGPipeline:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.index_path = os.path.join(VECTORSTORE_PATH, f"user_{user_id}_index.faiss")
        self.metadata_path = os.path.join(VECTORSTORE_PATH, f"user_{user_id}_metadata.json")
        self.chunks_path = os.path.join(VECTORSTORE_PATH, f"user_{user_id}_chunks.pkl")
        
        self.index = None
        self.metadata = []
        self.chunks = []
        
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                with open(self.chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
                logger.info(f"Loaded existing index for user {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self.index = None
        
        if self.index is None:
            # Create empty index with dimension 384 (MiniLM output)
            self.index = faiss.IndexFlatL2(384)
            self.metadata = []
            self.chunks = []
    
    def add_documents(self, texts: List[str], source: str) -> int:
        """Add documents to vector store"""
        try:
            # Generate embeddings
            embeddings = embedder.encode(texts, convert_to_numpy=True).astype('float32')
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store metadata
            for i, text in enumerate(texts):
                self.metadata.append({
                    "source": source,
                    "chunk_id": len(self.chunks)
                })
                self.chunks.append(text)
            
            # Save index
            self.save_index()
            logger.info(f"Added {len(texts)} chunks for user {self.user_id}")
            return len(texts)
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return 0
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Search vector store"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        try:
            # Encode query
            query_embedding = embedder.encode(query, convert_to_numpy=True).astype('float32').reshape(1, -1)
            
            # Search FAISS
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            # Return results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.chunks):
                    results.append((self.chunks[int(idx)], float(distance)))
            
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def save_index(self):
        """Save index to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def delete(self):
        """Delete user's vector store"""
        for path in [self.index_path, self.metadata_path, self.chunks_path]:
            if os.path.exists(path):
                os.remove(path)


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF"""
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX"""
    text = ""
    try:
        doc = DocxDocument(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        logger.error(f"Error reading DOCX: {e}")
    return text


def extract_text_from_txt(filepath: str) -> str:
    """Extract text from TXT"""
    text = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        logger.error(f"Error reading TXT: {e}")
    return text


def process_document(filepath: str, filename: str) -> str:
    """Process document based on file type"""
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(filepath)
    elif filename.endswith('.txt'):
        return extract_text_from_txt(filepath)
    else:
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(text)
