import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://catalog.iyte.edu.tr"

def clean_href(href):
    # Hatalı URL kısmını düzelt
    if "results.displaypanel.limitcolumn.navigatorclick" in href:
        href = href.replace(".displaypanel.limitcolumn.navigatorclick", "")
    return BASE_URL + href

def scrape_book_facets(page_url):
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "authors": [],
        "languages": [],
        "dates": [],
        "subjects": [],
        "locations": [],
        "libraries": []
    }

    def extract_facet(selector, key):
        spans = soup.select(selector)
        for a in spans:
            title = a.get("title", "").strip()
            href = a.get("href", "").strip()
            if title and href:
                result[key].append({
                    "title": title,
                    "url": clean_href(href)
                })

    extract_facet("#facetFormAUTHOR span a", "authors")
    extract_facet("#facetFormLANGUAGE span a", "languages")
    extract_facet("#facetFormPUBDATE span a", "dates")
    extract_facet("#facetFormSUBJECT span a", "subjects")
    extract_facet("#facetFormLOCATION span a", "locations")
    extract_facet("#facetFormLIBRARY span a", "libraries")

    return result

if __name__ == "__main__":
    url = "https://catalog.iyte.edu.tr/client/tr_TR/default_tr/search/results?rm=KITAP+KOLEKSIY0%7C%7C%7C1%7C%7C%7C0%7C%7C%7Ctrue&te=ILS"
    data = scrape_book_facets(url)

    with open("book_facets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Facet verileri 'book_facets.json' dosyasına kaydedildi.")
