import os 
import pandas as pd 
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def embbed_process(any_updated):
    if any_updated == True : 
        print("UPDATED DATA WILL BE PROCESEED")
        df = pd.read_csv(f"data/result-scrape.csv")
        df['all_text'] = df.apply(
            lambda row: f"Judul: {row['judul']}\n\nIsi: {row['isi']}\n\nSumber: {row['link']}",
            axis=1
        )
        documents = [
            Document(
                page_content=f"Judul: {row['judul']}\n\nIsi: {row['isi']}\n\nSumber: {row['link']}",
                metadata={"judul": row["judul"], "link": row["link"]}
            )
            for _, row in df.dropna(subset=['isi']).iterrows()
        ]

        # Gunakan model ST yang ringan dan cepat
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        # Simpan teks dalam FAISS dengan dokumen utuh (tanpa split)
        vectorstore = FAISS.from_documents(documents, embedding_model)
        retriever = vectorstore.as_retriever()
        vectorstore.save_local("faiss_store")
        print("faiss_store updated")
    else : 
        print("NOTHING UPDATED DATA, SO DON'T NEED TO UPDATED FAISS STORE")

if __name__ == "__main__":
    embbed_process()