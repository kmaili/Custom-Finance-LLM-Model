import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random
import base64
import os
import pdfkit
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

            # Remove scripts and potentially harmful elements
            for script in soup(["script", "noscript"]):
                script.decompose()

            # Preserve style tags
            for style_tag in soup.find_all('style'):
                style_tag.attrs = {k: v for k, v in style_tag.attrs.items() if k == 'type'}

            # Preserve inline styles and stylesheet links
            for tag in soup.find_all(True):
                # Keep inline styles
                if 'style' in tag.attrs:
                    # Optionally, you can add some basic sanitization here if needed
                    pass

                # Preserve stylesheet links
                if tag.name == 'link' and tag.get('rel') and 'stylesheet' in tag.get('rel'):
                    pass

            # Handle local images (same as before)
            for img in soup.find_all('img'):
                if img.get('src') and not img['src'].startswith(('data:', 'http', 'https')):
                    try:
                        with open(img['src'], 'rb') as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            img['src'] = f"data:image/jpeg;base64,{encoded_string}"
                    except Exception:
                        img.decompose()

            # Convert back to string, preserving the original structure
            cleaned_html = str(soup)
            return cleaned_html
        except Exception as e:
            print(f"HTML cleaning error: {e}")
            return html_content

    def html_to_pdf(self, iframe_html_content, filename):


        # Potential paths for wkhtmltopdf on different systems
        WKHTMLTOPDF_PATHS = [
            # Windows typical paths
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\wkhtmltopdf\wkhtmltopdf.exe',

            # macOS typical paths
            '/usr/local/bin/wkhtmltopdf',
            '/opt/homebrew/bin/wkhtmltopdf',

            # Linux typical paths
            '/usr/bin/wkhtmltopdf',
            '/usr/local/bin/wkhtmltopdf',
            '/snap/bin/wkhtmltopdf'
        ]

        # Find the first existing path
        wkhtmltopdf_path = None
        for path in WKHTMLTOPDF_PATHS:
            if os.path.exists(path):
                wkhtmltopdf_path = path
                break

        # If no path found, raise an informative error
        if not wkhtmltopdf_path:
            raise FileNotFoundError(
                "wkhtmltopdf executable not found. Please install it or provide the exact path. "
                "Download from: https://wkhtmltopdf.org/downloads.html"
            )

        # Create configuration with the found path
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        os.makedirs('PDFs', exist_ok=True)
        pdf_output_path = os.path.abspath(f'PDFs/{filename}.pdf')

        try:
            # Clean the HTML content
            cleaned_html = self.clean_html(iframe_html_content)

            # Parse the cleaned HTML
            soup = BeautifulSoup(cleaned_html, 'html.parser')

            # Add some basic styling to improve PDF rendering
            base_css = """
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-bottom: 10px; 
                }
                td, th { 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    word-wrap: break-word; 
                }
                img { 
                    max-width: 100%; 
                    height: auto; 
                }
            </style>
            """

            # Inject base CSS into the HTML
            if soup.head:
                css_tag = soup.new_tag('style')
                css_tag.string = base_css.strip('<style>').strip('</style>')
                soup.head.append(css_tag)
            else:
                head_tag = soup.new_tag('head')
                css_tag = soup.new_tag('style')
                css_tag.string = base_css.strip('<style>').strip('</style>')
                head_tag.append(css_tag)
                soup.html.insert(0, head_tag)

            # Convert soup back to string
            modified_html = str(soup)

            # Configuration options for pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }

            # Convert HTML to PDF
            pdfkit.from_string(
                modified_html,
                pdf_output_path,
                configuration=config,
                options=options
            )

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
