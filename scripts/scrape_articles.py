from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json

ARTICLE_URL = "https://gcris.iyte.edu.tr/simple-search?location=publications&crisID=&relationName=&query=&rpp=50&sort_by=bi_sort_2_sort&order=DESC"
BASE_URL = "https://gcris.iyte.edu.tr"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def extract_metadata_fields(soup):
    fields = {
        "title": "",
        "authors": "",
        "keywords": "",
        "abstract": ""
    }

    for tr in soup.select("table.itemDisplayTable tr"):
        label_td = tr.find("td", class_="metadataFieldLabel")
        value_td = tr.find("td", class_="metadataFieldValue")

        print(f"Processing row: {label_td.get_text(strip=True)}")
        if not label_td or not value_td:
            continue

        label = label_td.get_text(strip=True).lower()
        value = value_td.get_text(separator="; ", strip=True)

        if "title" in label:
            fields["title"] = value
        elif "authors" in label:
            fields["authors"] = value
        elif "keywords" in label:
            fields["keywords"] = value
        elif "abstract" in label:
            fields["abstract"] = value

    return fields


def scrape_articles(limit=1):
    driver = get_driver()
    driver.get(ARTICLE_URL)
    time.sleep(2)

    documents = []

    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")

        for i, row in enumerate(rows[1:limit+1]):
            try:
                link = row.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                driver.get(link)
                time.sleep(1.5)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                fields = extract_metadata_fields(soup)
                print(fields["title"])
                print(fields["authors"])
                print(fields["keywords"])
                print(fields["abstract"])

                title = fields["title"]
                authors = fields["authors"]
                keywords = fields["keywords"]
                abstract = fields["abstract"]

                combined_text = f"Title: {title}\nAuthors: {authors}\nKeywords: {keywords}\nAbstract: {abstract}"
                documents.append({
                    "id": f"article-{i}",
                    "text": combined_text,
                    "metadata": {
                        "title": title,
                        "authors": authors,
                        "keywords": keywords,
                        "abstract": abstract,
                        "category": "article",
                        "source_url": link
                    }
                })

                print(f"[{i+1}] ✅ {title}")

                driver.back()
                time.sleep(1)

            except Exception as e:
                print(f"[{i+1}] ❌ Error: {e}")
                continue

    finally:
        driver.quit()

    return documents

if __name__ == "__main__":
    data = scrape_articles()
    with open("data/raw/articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ Veriler 'articles.json' dosyasına kaydedildi.")
