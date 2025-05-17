from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

CATALOG_URL = "https://catalog.iyte.edu.tr/client/en_US/default/search/results?rm=BOOK+COLLECTION0%7C%7C%7C1%7C%7C%7C0%7C%7C%7Ctrue&te=ILS"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def scrape_book_locations(limit=30):
    driver = get_driver()
    driver.get(CATALOG_URL)
    time.sleep(3)

    books = []
    book_index = 0

    try:
        while len(books) < limit:
            for i in range(12):  # each page shows 12 books
                if len(books) >= limit:
                    break

                try:
                    link = driver.find_element(By.ID, f"detailLink{book_index}")
                    driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", link)

                    panel_id = f"tabDISCOVERY_ALLlistItem_twilightZone{book_index}"
                    WebDriverWait(driver, 10).until(
                        lambda d: d.find_element(By.ID, panel_id).get_attribute("innerHTML").strip() != ""
                    )
                    time.sleep(0.5)

                    panel = driver.find_element(By.ID, panel_id)
                    soup = BeautifulSoup(panel.get_attribute("innerHTML"), "html.parser")

                    title_tag = soup.select_one("div.text-p.INITIAL_TITLE_SRCH")
                    if not title_tag:
                        print(f"[!] Skipping book #{book_index+1} - Title not found")
                        continue
                    title = title_tag.get_text(strip=True)

                    author_tag = soup.select_one("div.text-p.INITIAL_AUTHOR_SRCH")
                    author = author_tag.get_text(strip=True) if author_tag else ""

                    row = soup.select_one("table.detailItemTable tbody tr")
                    if not row:
                        print(f"[!] Skipping book #{book_index+1} - Row not found")
                        continue

                    cols = row.find_all("td")
                    if len(cols) < 5:
                        print(f"[!] Skipping book #{book_index+1} - Incomplete data")
                        continue

                    library = next((div.get_text(strip=True) for div in cols[0].find_all("div") if "hidden" not in div.get("class", [])), "")
                    status = next((div.get_text(strip=True) for div in cols[4].find_all("div") if "hidden" not in div.get("class", [])), "")

                    books.append({
                        "id": f"book-{len(books)}",
                        "text": f"Title: {title}\nShelf: {cols[3].get_text(strip=True)}",
                        "metadata": {
                            "category": "book_location",
                            "title": title,
                            "author": author,
                            "library": library,
                            "material_type": cols[1].get_text(strip=True),
                            "barcode": cols[2].get_text(strip=True),
                            "shelf_number": cols[3].get_text(strip=True),
                            "status": status,
                            "source_url": CATALOG_URL
                        }
                    })

                    print(f"[{len(books)}] ✅ {title}")
                    book_index += 1

                    try:
                        close_btn = driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close")
                        close_btn.click()
                        time.sleep(0.5)
                    except:
                        pass

                except Exception as e:
                    print(f"[!] Error scraping book #{book_index+1}: {e}")
                    book_index += 1
                    continue

            # Next page
            if len(books) < limit:
                try:
                    next_btn = driver.find_element(By.ID, "NextPageBottom")
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(3)
                except:
                    print("No more pages.")
                    break

    finally:
        driver.quit()

    return books

if __name__ == "__main__":
    data = scrape_book_locations(limit=30)
    with open("data/raw/book_locations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ Veriler 'book_locations.json' dosyasına kaydedildi.")
