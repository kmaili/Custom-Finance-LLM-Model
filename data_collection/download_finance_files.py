from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import os
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from bs4 import BeautifulSoup


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
    'Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

class PDF_COLLECTOR:
    def clean_html(self, html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            for tag in soup.find_all(True):
                del tag['style']
            for img in soup.find_all('img'):
                if img.get('src') and not img['src'].startswith(('data:', 'http', 'https')):
                    try:
                        with open(img['src'], 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            img['src'] = f"data:image/jpeg;base64,{encoded_string}"
                    except Exception:
                        img.decompose()
            cleaned_html = str(soup)
            return cleaned_html
        except Exception as e:
            print(f"HTML cleaning error: {e}")
            return html_content

    def html_to_pdf(self, iframe_html_content, filename):
        os.makedirs('PDFs', exist_ok=True)
        pdf_output_path = os.path.abspath(f'PDFs/{filename}.pdf')
        try:
            cleaned_html = self.clean_html(iframe_html_content)
            pdf = SimpleDocTemplate(pdf_output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            soup = BeautifulSoup(cleaned_html, 'html.parser')
            for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = element.get_text(strip=True)
                if text:
                    if element.name.startswith('h'):
                        style = styles['Heading' + element.name[1]]
                    else:
                        style = styles['Normal']
                    story.append(Paragraph(text, style))
            pdf.build(story)
            print(f"PDF created successfully at {pdf_output_path}")
            return pdf_output_path
        except Exception as error:
            print(f"PDF conversion failed: {error}")
            raise ValueError(f"Could not convert HTML to PDF. Error: {error}")

    def initialize_driver(self):
        options = Options()
        random_user_agent = random.choice(USER_AGENTS)
        options.add_argument(f'user-agent={random_user_agent}')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--start-maximized')
        options.add_argument("--disable-blink-features=AutomationControlled")
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver.exe')
        service = Service(executable_path=chromedriver_path)
        return webdriver.Chrome(service=service, options=options)

    def save_full_html(self, driver, filename):
        try:
            self.html_to_pdf(driver.page_source, filename)
        except Exception as e:
            print(f"Error saving HTML files: {e}")

    def download_page_and_save_full_html(self, driver, url, filename):
        try:
            driver.get(url)
            time.sleep(2)
            self.save_full_html(driver, filename)
        except Exception as e:
            print(f"Error during download process for {url}: {e}")

    def collect_pdfs(self, urls_files_path):
        driver = self.initialize_driver()
        try:
            with open(urls_files_path, "r") as urls_file:
                html_pages_urls = urls_file.readlines()
            for index, url in enumerate(html_pages_urls):
                self.download_page_and_save_full_html(driver, url.strip(), f"file_{index}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()
