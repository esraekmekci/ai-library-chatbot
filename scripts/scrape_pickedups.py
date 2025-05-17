import requests
from bs4 import BeautifulSoup
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://library.iyte.edu.tr/en/quick-links/picked-ups-for-you/"

EXCLUDE_PATTERNS = [
    r"İYTE KÜTÜPHANE", r"IZTECH LIBRARY",
    r"@iyte\.edu\.tr", r"\+90\s?\d{3}", r"Gülbahçe Kampüsü", r"Urla"
]

def is_footer_line(text):
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def extract_filtered_content(url):
    try:
        resp = requests.get(url, verify=False, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        content_lines = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and not is_footer_line(text):
                content_lines.append(text)
        return content_lines

    except Exception as e:
        return []

def scrape_selected_for_you():
    try:
        resp = requests.get(URL, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        toggle_items = soup.find_all("div", class_="elementor-toggle-item")
        results = []

        for toggle in toggle_items:
            category_title_el = toggle.find("div", class_="elementor-tab-title")
            if not category_title_el:
                continue
            category = category_title_el.get_text(strip=True)
            results.append(f"=== {category} ===")

            content_el = toggle.find("div", class_="elementor-tab-content")
            if content_el:
                for link in content_el.find_all("a", href=True):
                    label = link.get_text(strip=True)
                    href = link["href"].strip()
                    results.append(f"--- {label} ({href}) ---")

                    content_lines = extract_filtered_content(href)
                    results.extend(content_lines)
                    results.append("")  # boşluk

        return results

    except Exception as e:
        return []

def scrape_pickedups():
    """
    Converts scraped selected books data into structured document chunks for indexing.
    Groups content by category and month.
    """
    # First get the raw results
    raw_results = scrape_selected_for_you()
    if not raw_results:
        return []
    
    documents = []
    current_category = ""
    current_month = ""
    current_month_url = ""
    current_books = []
    
    for line in raw_results:
        line = line.strip()
        
        # Category header
        if line.startswith("=== ") and line.endswith(" ==="):
            # Save previous category if there are books
            if current_books and current_category and current_month:
                formatted_text = f"Category: {current_category}\nMonth: {current_month}\nBooks:\n"
                formatted_text += "\n".join(current_books)
                
                documents.append({
                    "text": formatted_text,
                    "metadata": {
                        "category": current_category,
                        "month": current_month,
                        "source_url": current_month_url
                    }
                })
            
            # Start new category
            current_category = line.strip("= ")
            current_books = []
            current_month = ""
            current_month_url = ""
            
        # Month header
        elif line.startswith("--- ") and " (" in line and line.endswith(") ---"):
            # Save previous month if there are books
            if current_books and current_category and current_month:
                formatted_text = f"Category: {current_category}\nMonth: {current_month}\nBooks:\n"
                formatted_text += "\n".join(current_books)
                
                documents.append({
                    "text": formatted_text,
                    "metadata": {
                        "category": current_category,
                        "month": current_month,
                        "source_url": current_month_url
                    }
                })
            
            # Start new month
            parts = line.strip("- ").split(" (")
            current_month = parts[0]
            current_month_url = parts[1].rstrip(") ---")
            current_books = []
            
        # Book title
        elif line and not line.startswith("===") and not line.startswith("---") and not line.startswith("[Error"):
            current_books.append(line)
    
    # Don't forget the last group
    if current_books and current_category and current_month:
        formatted_text = f"Category: {current_category}\nMonth: {current_month}\nBooks:\n"
        formatted_text += "\n".join(current_books)
        
        documents.append({
            "text": formatted_text,
            "metadata": {
                "category": current_category,
                "month": current_month,
                "source_url": current_month_url
            }
        })
    
    return documents

