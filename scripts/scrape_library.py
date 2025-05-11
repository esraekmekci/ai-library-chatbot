import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://library.iyte.edu.tr/sikca-sorulan-sorular/"

def scrape_faqs():
    faqs = []
    try:
        response = requests.get(URL, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        questions = soup.find_all('div', class_='elementor-tab-title')
        answers = soup.find_all('div', class_='elementor-tab-content')

        for question, answer in zip(questions, answers):
                question_text = question.get_text(strip=True)
                answer_text = answer.get_text(strip=True)
                faqs.append({"question": question_text, "answer": answer_text})

        return faqs

    except Exception as e:
        print(f"Error: {e}")
        return faqs

if __name__ == "__main__":
    faq_data = scrape_faqs()

    if faq_data:
        with open("data/raw/faqs.txt", "w", encoding="utf-8") as f:
            for faq in faq_data:
                f.write(f"Question: {faq['question']}\nAnswer: {faq['answer']}\n\n")
        print("Data successfully scraped and saved to faqs_data.txt")
    else:
        print("No data scraped.")
