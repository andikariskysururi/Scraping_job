import requests
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from datetime import datetime 
def clean_detik_text(text):
    # 1️⃣ Hapus bagian SCROLL / ADVERTISEMENT / Simak Video
    text = re.sub(r'SCROLL TO CONTINUE WITH CONTENT', '', text, flags=re.IGNORECASE)
    text = re.sub(r'ADVERTISEMENT', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Simak Video.*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'\[Gambas:.*?\]', '', text, flags=re.IGNORECASE)

    # 2️⃣ Hapus "Baca juga: ..." (termasuk teks di belakangnya sampai titik pertama)
    text = re.sub(r'Baca juga:[^\n]*', '', text, flags=re.IGNORECASE)

    # 3️⃣ Hapus label halaman, seperti “Halaman 2 dari 2”
    text = re.sub(r'Halaman\s+\d+\s+dari\s+\d+', '', text, flags=re.IGNORECASE)

    # 4️⃣ Hapus bagian footer seperti "(dpw/dpw)" atau tag jurnalis
    text = re.sub(r'\([a-z]{2,5}/[a-z]{2,5}\)', '', text, flags=re.IGNORECASE)

    # 5️⃣ Hapus spasi / newline berlebihan
    text = re.sub(r'\n+', '\n', text)  # ganti multiple newline jadi satu
    text = re.sub(r'\s{2,}', ' ', text)  # ganti multiple spasi jadi satu
    text = text.strip()

    return text

def save_scrape_result(all_data):
    try : 
        df = pd.read_csv("data/result-scrape.csv")
    except : 
        df = pd.DataFrame()
    current_shape = df.shape[0]
    df2 = pd.DataFrame(all_data)
    df = pd.concat([df, df2])
    df = df.drop_duplicates(subset = 'link')
    after_update_shape = df.shape[0]
    updated_n_rows = after_update_shape - current_shape
    if (updated_n_rows) > 0: 
        print(f"UPDATED DATA {datetime.now()} : {updated_n_rows} ARTIKEL")
        df.to_csv(f"data/result-scrape.csv")
        return True
    else : 
        print("NOTHING UPDATED DATA")
        return False

def scraper_engine(n_data = 10): 
    all_data = []

    for page in tqdm(range(0, n_data)):  # ambil 100 halaman pencarian
        url = f'https://www.detik.com/search/searchall?query=pajak%20umkm&page={page}&result_type=relevansi'
        res = requests.get(url)
        soup = bs(res.content, 'html.parser')

        title = soup.find_all('h3', class_="media__title")
        if not title:
            break  # stop kalau sudah tidak ada hasil

        for t in title:
            a_tag = t.find('a')
            if not a_tag:
                continue
            link = a_tag.get('href')
            judul = a_tag.get_text(strip=True)

            # ambil isi artikel langsung
            try:
                r = requests.get(link, timeout=10)
                soup_artikel = bs(r.content, 'html.parser')
                content = soup_artikel.find('div', class_="detail__body-text")
                if not content:
                    content = soup_artikel.find('div', class_="detail__content-text")

                if content:
                    raw_text = content.get_text(separator="\n", strip=True)
                    clean_text = clean_detik_text(raw_text)
                else:
                    clean_text = ''

                all_data.append({
                    'judul': judul,
                    'link': link,
                    'isi': clean_text
                })

            except Exception as e:
                print(f"❌ Error ambil isi dari {link}: {e}")
                continue

    print(f"\n SCRAPED DATA TOTAL: {len(all_data)} ARTIKEL")
    any_updated = save_scrape_result(all_data) 
    return any_updated

if __name__ == "__main__":
    scraper_engine()