import re

import pdfplumber


def extract_text_without_tables(pdf_path):
    """
    Extract text from a PDF while removing tables.

    :param pdf_path: Path to the PDF file
    :return: Cleaned text without tables
    """
    cleaned_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Identify tables on the page
            tables = page.find_tables()
            table_bounds = [table.bbox for table in tables]

            # Extract text excluding table regions
            non_table_text = page.filter(lambda obj: not __is_within_table(obj, table_bounds)).extract_text()

            if non_table_text:
                cleaned_text += non_table_text + "\n"

    return cleaned_text


def __is_within_table(obj, table_bounds):
    """
    Check if an object (e.g., a text box) is within any table bounds.

    :param obj: Object to check
    :param table_bounds: List of table bounding boxes
    :return: True if the object is within any table, otherwise False
    """
    x0, y0, x1, y1 = obj.get("x0", 0), obj.get("top", 0), obj.get("x1", 0), obj.get("bottom", 0)
    for bounds in table_bounds:
        bx0, by0, bx1, by1 = bounds
        if bx0 <= x0 <= bx1 and by0 <= y0 <= by1:
            return True
    return False


def remove_headers_and_footers(text, start_marker, end_marker):
    """
    Removes repeated headers and footers from the text.

    :param text: Raw text
    :param start_marker: A marker string; all text above this marker will be removed
    :param end_marker: A marker string; all text below this marker will be removed
    :return: Text without headers and footers
    """
    text = re.sub(f".*?{re.escape(start_marker)}", start_marker, text, flags=re.DOTALL)
    text = re.sub(f"{re.escape(end_marker)}.*", "", text, flags=re.DOTALL)
    text = re.sub(r"Page \d+", "", text)  # Removes "Page X"
    return text

def normalize_whitespace(text):
    """
    Normalizes whitespace by replacing multiple spaces and line breaks with single spaces.

    :param text: Text to normalize
    :return: Normalized text
    """
    return re.sub(r"\s+", " ", text)


def clean_broken_lines(text):
    """
    Fixes broken lines in the text by merging lines not ending with punctuation.

    :param text: Text with broken lines
    :return: Text with fixed lines
    """
    return re.sub(r"(?<!\.)\n", " ", text)


def remove_irrelevant_sections(text):
    """
    Removes irrelevant sections such as disclaimers and boilerplate text.

    :param text: Raw text
    :return: Cleaned text
    """
    text = re.sub(r"Forward-Looking Statements.*?(?=\n[A-Z])", "", text, flags=re.DOTALL)
    return text