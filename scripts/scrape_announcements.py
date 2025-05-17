import requests
from bs4 import BeautifulSoup, NavigableString
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://library.iyte.edu.tr/en/duyuru/"

def scrape_announcements(max_items=20):
    announcements = []
    try:
        response = requests.get(URL, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        list_items = soup.find_all("li", class_="newsbox__list-item")

        for i, li in enumerate(list_items[:max_items]):
            a_tag = li.find("a", class_="newsitem")
            if not a_tag:
                continue
            detail_url = a_tag["href"]
            title = a_tag.find("p", class_="newsitem__excerpt").get_text(strip=True)

            #fetching the detail page
            detail_response = requests.get(detail_url, verify=False)
            detail_response.raise_for_status()
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

            full_title = detail_soup.find("h1", class_="post_title").get_text(strip=True)

            date = detail_soup.find("div", class_="postmeta__date").get_text(strip=True)

            content_div = detail_soup.find("section", class_="wysiwyg vanilla")
            paragraphs = content_div.find_all(["p", "h3"])
            full_text = extract_rich_text(content_div)

            announcements.append({
                "id": f"announcement-{i}",
                "text": f"{full_title}\n{full_text}",
                "metadata": {
                    "title": full_title,
                    "category": "announcement",
                    "body": full_text,
                    "source_url": detail_url
                }
            })

    except Exception as e:
        print(f"Error scraping announcements: {e}")

    return announcements


def extract_rich_text(element):
    """Extract clean, unique visible text from HTML content. Avoids double-parsing nested elements."""
    seen = set()
    output = []

    def walk(el):
        if isinstance(el, NavigableString):
            text = el.strip()
            if text and text not in seen:
                seen.add(text)
                output.append(text)
            return

        if el.name in ["script", "style"]:
            return

        # A tag: add text + URL
        if el.name == "a":
            link_text = el.get_text(strip=True)
            href = el.get("href", "").strip()
            full = f"{link_text} ({href})" if href else link_text
            if full and full not in seen:
                seen.add(full)
                output.append(full)
            return

        # Children varsa onları işle (yani parent'ın get_text'ini alma!)
        if hasattr(el, "children"):
            for child in el.children:
                walk(child)

    walk(element)

    return "\n".join(output)



# if __name__ == "__main__":
#     ann_data = scrape_announcements()

#     if ann_data:
#         with open("data/raw/announcements.txt", "w", encoding="utf-8") as f:
#             for ann in ann_data:
#                 f.write(f"Announcement: {ann}\n\n")
#         print("Data successfully scraped and saved to announcements.txt")
#     else:
#         print("No data scraped.")