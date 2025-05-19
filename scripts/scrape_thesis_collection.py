import requests
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://catalog.iyte.edu.tr"
PAGE_URL = "https://catalog.iyte.edu.tr/client/en_US/default/search/results?rm=THESIS+COLLECT0%7C%7C%7C1%7C%7C%7C0%7C%7C%7Ctrue&te=ILS"

def clean_href(href):
    if "results.displaypanel.limitcolumn.navigatorclick" in href:
        href = href.replace(".displaypanel.limitcolumn.navigatorclick", "")
    return BASE_URL + href

def generate_text(category, title):
    if category == "authors":
        return f"You can find theses written by {title} from this link."
    elif category == "dates":
        return f"You can find theses published in {title} from this link."
    elif category == "subjects":
        return f"You can find theses about {title} from this link."
    else:
        return f"You can find theses related to {title} in {category} category from this link."

def scrape_thesis_facets():
    response = requests.get(PAGE_URL, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    categories = {
        "authors": "#facetFormAUTHOR #facetAUTHOR span > a",
        "dates": "#facetFormPUBDATE #facetPUBDATE span > a",
        "subjects": "#facetFormSUBJECT #facetSUBJECT span > a"
    }

    for category, selector in categories.items():
        links = soup.select(selector)
        for i, a in enumerate(links):
            title = a.get("title", "").strip()
            href = a.get("href", "").strip()
            if title and href:
                url = clean_href(href)
                data.append({
                    "id": f"{category}-{i}",
                    "text": generate_text(category, title),
                    "metadata": {
                        "category": category,
                        "title": title,
                        "source_url": url
                    }
                })

    return data

if __name__ == "__main__":
    data = scrape_thesis_facets()

    with open("thesis_facets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Facet verileri 'thesis_facets.json' dosyasına kaydedildi.")
