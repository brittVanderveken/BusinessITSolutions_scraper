business-it-workshop


import requests
import pandas as pd
from bs4 import BeautifulSoup
from google.colab import files
uploaded = files.upload()

with open("hollister.html", encoding="utf-8", errors="replace") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

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

from datetime import datetime
import os

scrape_time = datetime.now().isoformat()
df["scraped_datum"] = scrape_time


filename = "hollister_dataset.csv"
if os.path.exists(filename):
    df.to_csv(filename, mode="a", header=False, index=False)
else:
    df.to_csv(filename, index=False)

print(f"{len(df)} rijen toegevoegd — CSV heeft nu historische data")



from supabase import create_client
from datetime import datetime

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
