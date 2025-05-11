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

        for i, (question, answer) in enumerate(zip(questions, answers)):
                question_text = question.get_text(strip=True)
                answer_text = answer.get_text(strip=True)
                faqs.append(
                    {"id": f"faq-{i}",
                     "text": f"Question: {question_text}\nAnswer: {answer_text}",
                     "metadata": {
                        "category": "FAQ",
                        "question": question_text,
                        "answer": answer_text,
                        "source_url": URL
                     }
                    })

    except Exception as e:
        print(f"Error scraping FAQs: {e}")

    return faqs

