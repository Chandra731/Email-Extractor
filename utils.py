import fitz  # PyMuPDF
import re
from email_validator import validate_email, EmailNotValidError
import pandas as pd
from io import BytesIO
import pytesseract
from PIL import Image
import docx
import requests
from bs4 import BeautifulSoup
import tempfile
import os

def extract_text_from_pdf(file) -> str:
    """Extract text from all pages of a PDF file object, with OCR fallback."""
    file_bytes = file.read()
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        file.seek(0)
        raise e

    text = ""
    for page in doc:
        page_text = page.get_text()
        if not page_text.strip():
            # OCR fallback for scanned pages
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            text += ocr_text
        else:
            text += page_text
    doc.close()
    file.seek(0)  # Reset file pointer for reuse if needed
    return text

def extract_text_from_docx(file) -> str:
    """Extract text from a DOCX file object."""
    file.seek(0)
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_txt(file) -> str:
    """Extract text from a TXT file object."""
    file.seek(0)
    return file.read().decode("utf-8", errors="ignore")

def extract_text_from_url(url: str) -> str:
    """Extract visible text from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)
        return text
    except Exception:
        return ""

def extract_emails_from_url_recursive(url: str, max_pages=20) -> set:
    """
    Recursively scrape emails from the given URL and its sublinks within the same domain.
    Limits to max_pages to avoid excessive crawling.
    """
    from urllib.parse import urlparse, urljoin
    visited = set()
    emails = set()
    domain = urlparse(url).netloc

    def crawl(url_to_crawl):
        if len(visited) >= max_pages or url_to_crawl in visited:
            return
        try:
            response = requests.get(url_to_crawl, timeout=10)
            response.raise_for_status()
            visited.add(url_to_crawl)
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract emails from page text
            text = soup.get_text(separator="\n")
            page_emails = set(extract_emails(text))
            emails.update(page_emails)
            # Find all links within the same domain
            for link in soup.find_all("a", href=True):
                href = link['href']
                full_url = urljoin(url_to_crawl, href)
                parsed_url = urlparse(full_url)
                if parsed_url.netloc == domain and full_url not in visited:
                    crawl(full_url)
        except Exception:
            pass

    crawl(url)
    return emails

def extract_emails(text) -> list:
    """Extract, validate, deduplicate, and sort emails from text."""
    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    potential_emails = set(re.findall(email_pattern, text))

    valid_emails = set()
    for email in potential_emails:
        try:
            v = validate_email(email)
            valid_emails.add(v.email)
        except EmailNotValidError:
            continue

    return sorted(valid_emails)

def export_emails_to_csv(email_list) -> BytesIO:
    """Convert email list to CSV encoded buffer."""
    df = pd.DataFrame(email_list, columns=["Email"])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

def export_emails_to_txt(email_list) -> BytesIO:
    """Convert email list to TXT encoded buffer."""
    txt_buffer = BytesIO()
    txt_buffer.write("\n".join(email_list).encode("utf-8"))
    txt_buffer.seek(0)
    return txt_buffer
