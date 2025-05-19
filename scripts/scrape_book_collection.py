import requests
from bs4 import BeautifulSoup
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://catalog.iyte.edu.tr"
PAGE_URL = "https://catalog.iyte.edu.tr/client/en_US/default/search/results?rm=BOOK+COLLECTION0%7C%7C%7C1%7C%7C%7C0%7C%7C%7Ctrue&te=ILS"

def clean_href(href):
    if "results.displaypanel.limitcolumn.navigatorclick" in href:
        href = href.replace(".displaypanel.limitcolumn.navigatorclick", "")
    return BASE_URL + href

def scrape_book_facets():
    try:
        response = requests.get(PAGE_URL, verify=False)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    all_facets = []
    facet_types = {
        "authors": "#facetFormAUTHOR span a",
        "languages": "#facetFormLANGUAGE span a",
        "dates": "#facetFormPUBDATE span a",
        "subjects": "#facetFormSUBJECT span a",
        "locations": "#facetFormLOCATION span a",
        "libraries": "#facetFormLIBRARY span a"
    }

    idx = 0
    for category, selector in facet_types.items():
        links = soup.select(selector)
        for link in links:
            title = link.get("title", "").strip()
            href = link.get("href", "").strip()
            if title and href:
                all_facets.append({
                    "id": f"{category}-{idx}",
                    "text": generate_text(category, title),
                    "metadata": {
                        "category": category,
                        "name": title,
                        "source_url": clean_href(href)
                    }
                })
                idx += 1

    return all_facets

def generate_text(category, title):
    if category == "authors":
        return f"You can find books written by {title} from this link."
    elif category == "languages":
        return f"You can find books written in {title} language from this link."
    elif category == "dates":
        return f"You can find books published in {title} from this link."
    elif category == "subjects":
        return f"You can find books about {title} from this link."
    elif category == "locations":
        return f"You can find books located in {title} from this link."
    elif category == "libraries":
        return f"You can find books available at {title} library from this link."
    else:
        return f"You can find books related to {title} in {category} category from this link."
    
if __name__ == "__main__":
    data = scrape_book_facets()

    with open("book_facets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Facet verileri 'book_facets.json' dosyasına kaydedildi.")
