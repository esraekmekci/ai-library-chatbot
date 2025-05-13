from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import time

BASE_URL = "https://libguides.iyte.edu.tr/?b=g&d=a"

def extract_rich_text(element):
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

        if el.name == "a":
            link_text = el.get_text(strip=True)
            href = el.get("href", "").strip()
            full = f"{link_text} ({href})" if href else link_text
            if full and full not in seen:
                seen.add(full)
                output.append(full)
            return

        if hasattr(el, "children"):
            for child in el.children:
                walk(child)

    walk(element)
    return "\n".join(output)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def get_guide_links(driver, max_items=100):
    driver.get(BASE_URL)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []
    for div in soup.find_all("div", class_="s-lg-gtitle")[:max_items]:
        a = div.find("a", class_="bold", href=True)
        if a:
            links.append((a.get_text(strip=True), urljoin(BASE_URL, a["href"])))
    return links

def scrape_all_tabs(driver, guide_url):
    driver.get(guide_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    tab_links = set()
    ul = soup.find("ul", class_="nav-tabs")
    if ul:
        for li in ul.find_all("li"):
            main_a = li.find("a", href=True)
            if main_a:
                tab_links.add(urljoin(guide_url, main_a["href"]))
            dropdown_ul = li.find("ul", class_="s-lg-subtab-ul")
            if dropdown_ul:
                for sub_a in dropdown_ul.find_all("a", href=True):
                    tab_links.add(urljoin(guide_url, sub_a["href"]))
    else:
        tab_links = {guide_url}

    all_texts = []

    for tab_url in tab_links:
        try:
            driver.get(tab_url)
            print(f"Scraping tab: {tab_url}")
            time.sleep(2)
            tab_soup = BeautifulSoup(driver.page_source, "html.parser")
            blocks = tab_soup.find_all("div", class_="s-lib-main")
            print(f"Found {len(blocks)} blocks in tab: {tab_url}")
            content = "\n\n".join([extract_rich_text(div) for div in blocks])
            print(f"Extracted {len(content)} characters from tab: {tab_url}")
            all_texts.append(content)
        except Exception as e:
            print(f"[!] Failed to scrape tab: {tab_url}\n    Error: {e}")
            continue

    return "\n\n".join(all_texts)

def scrape_guides(max_items=100):
    driver = get_driver()
    guides = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    try:
        guide_links = get_guide_links(driver, max_items)

        for i, (title, guide_url) in enumerate(guide_links):
            print(f"Scraping [{i+1}/{len(guide_links)}]: {title}")
            try:
                full_text = scrape_all_tabs(driver, guide_url)
                print(f"Scraped {len(full_text)} characters from {title}")
                
                chunks = splitter.split_text(full_text)
                
                for j, chunk in enumerate(chunks):
                    guides.append({
                        "id": f"guide-{i}-{j}",
                        "text": chunk,
                        "metadata": {
                            "title": title,
                            "category": "guide",
                            "source_url": guide_url
                        }
                    })
            except Exception as e:
                print(f"[!] Skipped guide '{title}' due to error:\n    {e}")
                continue

    finally:
        driver.quit()

    return guides

if __name__ == "__main__":
    data = scrape_guides()
    if data:
        with open("data/raw/guides.txt", "w", encoding="utf-8") as f:
            for guide in data:
                f.write(f"Guide: {guide}\n\n")
        print("Data successfully scraped and saved to guides.txt")
    else:
        print("No data scraped.")
    
