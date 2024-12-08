import re

import bs4
import pdfkit
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import random

from xhtml2pdf import pisa

# List of User-Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

import os
import io
import re
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from bs4 import BeautifulSoup


def clean_html(html_content):
    """
    Preprocess HTML to remove problematic CSS and clean up content

    Args:
    html_content (str): Original HTML content

    Returns:
    str: Cleaned HTML content
    """
    try:
        # Use BeautifulSoup to parse and clean the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script tags
        for script in soup(["script", "style"]):
            script.decompose()

        # Clean up CSS
        for tag in soup.find_all(True):
            # Remove inline styles that might cause parsing issues
            del tag['style']

        # Convert images to base64 if needed
        for img in soup.find_all('img'):
            if img.get('src') and not img['src'].startswith(('data:', 'http', 'https')):
                try:
                    with open(img['src'], 'rb') as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        img['src'] = f"data:image/jpeg;base64,{encoded_string}"
                except Exception:
                    # Remove image if can't be converted
                    img.decompose()

        # Convert to string
        cleaned_html = str(soup)

        return cleaned_html

    except Exception as e:
        print(f"HTML cleaning error: {e}")
        return html_content


def html_to_pdf(iframe_html_content, filename):
    """
    Convert HTML content to PDF using reportlab

    Args:
    iframe_html_content (str): HTML content to convert
    filename (str): Output PDF filename (without .pdf extension)

    Returns:
    str: Path to the generated PDF file
    """
    # Ensure output directory exists
    os.makedirs('PDFs', exist_ok=True)

    # Full output path
    pdf_output_path = os.path.abspath(f'PDFs/{filename}.pdf')

    try:
        # Clean the HTML content
        cleaned_html = clean_html(iframe_html_content)

        # Create a PDF
        pdf = SimpleDocTemplate(pdf_output_path, pagesize=letter)

        # Style for paragraphs
        styles = getSampleStyleSheet()

        # Convert HTML to PDF-compatible paragraphs
        story = []
        soup = BeautifulSoup(cleaned_html, 'html.parser')

        # Extract text content
        for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = element.get_text(strip=True)
            if text:
                # Choose appropriate style based on tag
                if element.name.startswith('h'):
                    style = styles['Heading' + element.name[1]]
                else:
                    style = styles['Normal']

                story.append(Paragraph(text, style))

        # Build PDF
        pdf.build(story)

        print(f"PDF created successfully at {pdf_output_path}")
        return pdf_output_path

    except Exception as error:
        print(f"PDF conversion failed: {error}")
        raise ValueError(f"Could not convert HTML to PDF. Error: {error}")


def initialize_driver():
    options = Options()
    # Select a random User-Agent
    random_user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={random_user_agent}')
    # options.add_argument('--headless')  # Uncomment to run headless
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--start-maximized')
    # Prevent WebDriver detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver_path = 'chromedriver.exe'  # Update with your ChromeDriver path
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)


def save_full_html(driver, filename):
    try:
        # Wait for the page to fully load
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # Wait for iframe to load
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'ixvFrame'))
        )

        # Switch to iframe and wait for its content to load
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # Additional wait to ensure dynamic content is loaded
        time.sleep(5)

        # Get the full HTML content of the iframe
        iframe_html_content = driver.execute_script("""
            return document.documentElement.outerHTML;
        """)

        # Switch back to default content
        driver.switch_to.default_content()


        html_to_pdf(iframe_html_content, filename)

    except Exception as e:
        print(f"Error saving HTML files: {e}")


def download_page_and_save_full_html(driver, url, filename):
    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for initial page load
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # Save the full HTML content to files
        save_full_html(driver, filename)

    except Exception as e:
        print(f"Error during download process for {url}: {e}")


# Main execution
def main():
    # Initialize the WebDriver
    driver = initialize_driver()

    try:
        # Read URLs from file
        with open("URLs.txt", "r") as urls_file:
            html_pages_urls = urls_file.readlines()

        # Download and save HTML for each URL
        for index, url in enumerate(html_pages_urls):
            download_page_and_save_full_html(driver, url.strip(), f"file_{index}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Always ensure the driver is closed
        driver.quit()


if __name__ == "__main__":
    main()