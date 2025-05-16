import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://catalog.iyte.edu.tr"

def clean_href(href):
    # Yanlış şablonu düzelt
    if "results.displaypanel.limitcolumn.navigatorclick" in href:
        href = href.replace(".displaypanel.limitcolumn.navigatorclick", "")
    return BASE_URL + href

def scrape_thesis_facets(page_url):
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "authors": [],
        "dates": [],
        "subjects": []
    }

    # Yazarlar
    author_spans = soup.select("#facetFormAUTHOR #facetAUTHOR span > a")
    for a in author_spans:
        title = a.get("title", "").strip()
        href = a.get("href", "").strip()
        if title and href:
            result["authors"].append({
                "title": title,
                "url": clean_href(href)
            })

    # Yayın tarihleri
    date_spans = soup.select("#facetFormPUBDATE #facetPUBDATE span > a")
    for a in date_spans:
        title = a.get("title", "").strip()
        href = a.get("href", "").strip()
        if title and href:
            result["dates"].append({
                "title": title,
                "url": clean_href(href)
            })

    # Konular
    subject_spans = soup.select("#facetFormSUBJECT #facetSUBJECT span > a")
    for a in subject_spans:
        title = a.get("title", "").strip()
        href = a.get("href", "").strip()
        if title and href:
            result["subjects"].append({
                "title": title,
                "url": clean_href(href)
            })

    return result

if __name__ == "__main__":
    url = "https://catalog.iyte.edu.tr/client/tr_TR/default_tr/search/results?rm=TEZ+KOLEKSIYONU0%7C%7C%7C1%7C%7C%7C0%7C%7C%7Ctrue&te=ILS"
    data = scrape_thesis_facets(url)

    with open("thesis_facets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nVeriler 'thesis_facets.json' dosyasına kaydedildi.")
