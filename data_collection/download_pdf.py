import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random
import base64
import os
from selenium.webdriver.support.wait import WebDriverWait

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
        options.add_argument("--print-to-pdf")

        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../chromedriver.exe')
        service = Service(executable_path=chromedriver_path)
        return webdriver.Chrome(service=service, options=options)

    def scroll_page_thoroughly(self, driver):
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def download_page_and_save_full_html(self, driver, url, filename):
        try:
            driver.get(url)
            time.sleep(3)
            self.scroll_page_thoroughly(driver)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            driver.execute_script("""
                    var style = document.createElement('style');
                    style.textContent = `
                        @media print {
                            * {
                                -webkit-print-color-adjust: exact !important;
                                color-adjust: exact !important;
                                print-color-adjust: exact !important;
                            }
                        }
                    `;
                    document.head.appendChild(style);
                """)
            pdf = driver.execute_cdp_cmd('Page.printToPDF', {
                'scale': 1,
                'paperWidth': 8.5,
                'paperHeight': 11,
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
                'printPageBackground': True,
                'transferMode': 'ReturnAsBase64',
                'marginTop': 0,
                'marginBottom': 0,
                'marginLeft': 0,
                'marginRight': 0
            })
            pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fr'..\PDFs\{filename}.pdf')
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            with open(pdf_path, 'wb') as f:
                f.write(base64.b64decode(pdf['data']))
            print(f"{filename} saved")
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
