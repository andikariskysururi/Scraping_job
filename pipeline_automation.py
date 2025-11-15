import os
import time
from scraper import scraper_engine
from embedder import embbed_process
from huggingface_hub import HfApi, upload_folder

from dotenv import load_dotenv
load_dotenv()

#push to HG 
HF_TOKEN = os.getenv("HF_TOKEN")  # simpan token di env (ga hardcode)
REPO_ID = "andikarisky28/scraping-job-rag"  # space kamu
print(HF_TOKEN)
def run_pipeline():
    #scrapping 
    print('runn scrapping')
    scraper_engine()

    #embedding 
    print('runm embbed')
    embbed_process()
    

    print(">> Uploading FAISS Store to Hugging Face...")

    api = HfApi()
    upload_folder(
        repo_id=REPO_ID,
        token=HF_TOKEN,
        folder_path="faiss_store",
        repo_type="space",
        allow_patterns=["*.faiss", "*.pkl"]
    )
    
    print(">> Upload complete!")


if __name__ == "__main__":
    run_pipeline()