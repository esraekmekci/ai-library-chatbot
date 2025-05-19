from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json

URL = "https://libguides.iyte.edu.tr/az/databases"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def scrape_databases():
    driver = get_driver()
    driver.get(URL)
    time.sleep(3)

    view_more_buttons = driver.find_elements(By.CLASS_NAME, "az-description-view-more")
    for btn in view_more_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.1)
        except Exception:
            continue

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.select("div.az-item")
    databases = []

    for i, item in enumerate(items):
        try:
            title_tag = item.select_one("a.az-title")
            description_tag = item.select_one("div.az-description")

            if not title_tag or not description_tag:
                continue

            name = title_tag.get_text(strip=True)
            href = title_tag.get("href", "").strip()
            description = description_tag.get_text(strip=True)

            databases.append({
                "id": f"database-{i}",
                "text": f"Database: {name}\nDescription: {description}",
                "metadata": {
                    "category": "database",
                    "name": name,
                    "description": description,
                    "source_url": href
                }
            })
        except Exception as e:
            print(f"[!] Error on item #{i}: {e}")
            continue

    driver.quit()
    return databases

if __name__ == "__main__":
    data = scrape_databases()
    with open("databases.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ Veriler 'databases.json' dosyasına kaydedildi.")
