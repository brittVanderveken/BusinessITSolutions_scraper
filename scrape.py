
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client
import os
import requests
from bs4 import BeautifulSoup

url = "https://www.hollisterco.com/shop/eu-nl/dames-nieuw-binnen"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser"

rows = []
for item in soup.select('[data-testid="catalog-product-card"]'):
    naam_el  = item.select_one('[data-testid="catalog-product-card-name"]')
    prijs_el = item.select_one('[data-testid="product-price-text-wrapper"]')
    naam  = naam_el.get_text(strip=True) if naam_el  else None
    prijs = prijs_el.get_text(strip=True) if prijs_el else None
    rows.append({"naam": naam, "prijs": prijs})

df = pd.DataFrame(rows)
print(f"{len(df)} producten gevonden")


df["prijs_eur"] = (
    df["prijs"]
    .str.replace("€", "", regex=False)
    .str.strip()
    .str.replace(",", ".")
    .str.replace(r"[^\d.]", "", regex=True)
    .astype(float)
)



df["naam"] = df["naam"].fillna("Onbekend")

df = df.rename(columns={
    "prijs": "prijs_rauw",
    "naam":  "product_naam",
})



df.to_csv("verify_output.csv", index=False)
print(f"Rows: {len(df)}  |  Columns: {list(df.columns)}")
df



scrape_time = datetime.now().isoformat()
df["scraped_datum"] = scrape_time


filename = "hollister_dataset.csv"
if os.path.exists(filename):
    df.to_csv(filename, mode="a", header=False, index=False)
else:
    df.to_csv(filename, index=False)

print(f"{len(df)} rijen toegevoegd — CSV heeft nu historische data")





SUPABASE_URL = "https://rbialmhxdmcdjeqlevml.supabase.co"
SUPABASE_KEY = "sb_publishable_4_vjkZxAPYSwr0tD9HcwFA__4gCWpM2"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
scrape_time = datetime.now().isoformat()

rows = []
for _, row in df.iterrows():
    rows.append({
        "product_naam": str(row.get("product_naam", "")),
        "prijs_rauw":   str(row.get("prijs_rauw", "")),
        "prijs_eur":    float(row.get("prijs_eur", 0)),
        "scraped_datum":   scrape_time,
    })

result = supabase.table("hollister_producten").insert(rows).execute()
print(f"{len(rows)} rijen ingevoegd in Supabase")
