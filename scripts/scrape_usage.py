import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://library.iyte.edu.tr/en/about-us/conditions-of-use/"
#OUTPUT_FILE = "cleaned_yararlanma_kosullari_structured.txt"

def scrape_conditions_of_use():
    try:
        resp = requests.get(URL, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        main_section = soup.find("section", class_="wysiwyg vanilla")
        if not main_section:
            print("Main content section not found.")
            return []

        output_lines = []
        seen = set()
        current_main_title = ""
        current_subsection = ""

        def emit_main_title(t):
            nonlocal current_main_title
            t = t.strip()
            if t and t != current_main_title:
                current_main_title = t

        for el in main_section.find_all(recursive=True):
            # Main title: <strong>
            if el.name == "strong":
                emit_main_title(el.get_text(strip=True))
                current_subsection = ""  # reset subsection

            # Subsection: Accordion title
            elif el.has_attr("class") and "elementor-tab-title" in el["class"]:
                current_subsection = el.get_text(strip=True)

            # Accordion content
            elif el.has_attr("class") and "elementor-tab-content" in el["class"]:
                if el.find("table"):
                    continue  # tables handled below
                lines = el.get_text(separator="\n", strip=True).split("\n")
                for line in lines:
                    line = line.strip()
                    if line and line not in seen:
                        output_lines.append((line, current_main_title, current_subsection))
                        seen.add(line)

            # Paragraphs (not in tables)
            elif el.name == "p" and not el.find_parent("table"):
                text = el.get_text(strip=True)
                if text and text not in seen:
                    if not el.find_parent(class_="elementor-tab-content"):
                        current_subsection = ""
                    output_lines.append((text, current_main_title, current_subsection))
                    seen.add(text)

            # Tables
            elif el.name == "table":
                if not el.find_parent(class_="elementor-tab-content"):
                    current_subsection = ""
                for row in el.find_all("tr"):
                    cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    if cells:
                        row_text = " | ".join(cells)
                        if row_text and row_text not in seen:
                            output_lines.append((row_text, current_main_title, current_subsection))
                            seen.add(row_text)

            # Links
            elif el.name == "a" and el.get("href"):
                label = el.get_text(strip=True)
                href = el["href"].strip()
                link = f"{label} ({href})"
                if label and link not in seen:
                    output_lines.append((link, current_main_title, ""))
                    seen.add(link)

        # === Save to .txt (commented out for control)
        # with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        #     for line, title, section in output_lines:
        #         if section:
        #             f.write(f"=== {title} | {section} ===\n{line}\n\n")
        #         else:
        #             f.write(f"=== {title} ===\n{line}\n\n")

        # print(f"Output written to: {OUTPUT_FILE}")

        return output_lines

    except Exception as e:
        print(f"Error: {e}")
        return []


def scrape_usage():
    """
    Converts scraped lines into structured document chunks for indexing.
    Groups content by (main_title, subsection).
    Includes title and section in the document text for better context.
    """
    output_lines = scrape_conditions_of_use()
    if not output_lines:
        return []

    documents = []
    grouped = {}

    for text, title, section in output_lines:
        key = (title.strip(), section.strip() or None)
        grouped.setdefault(key, []).append(text)

    for (title, section), lines in grouped.items():
        # Create a formatted text that includes title and section for context
        formatted_text = f"Title: {title}\n"
        if section:
            formatted_text += f"Section: {section}\n"
        formatted_text += "Content:\n" + "\n".join(lines)
        
        documents.append({
            "text": formatted_text,
            "metadata": {
                "title": title,
                "section": section or "",
                "source_url": URL
            }
        })

    print(f"Prepared {len(documents)} documents for indexing.")
    return documents

