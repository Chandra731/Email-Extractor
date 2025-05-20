# Email Extractor from PDFs and URLs

![Demo Screenshot](assets/demo_screenshot.png)

## Features

- Upload multiple PDF, DOCX, and TXT files to extract emails.
- Recursive URL scraping: extract emails from root URL and sublinks within the same domain.
- OCR support for scanned PDFs using Tesseract OCR.
- Encrypted PDF handling.
- Advanced email validation and deduplication.
- Display emails per source in expandable sections with tables.
- Download combined emails as CSV or TXT files.
- Responsive error handling for corrupted or empty files.
- Clean, user-friendly Streamlit interface with sidebar tips.
- Progress bar during URL scraping.
- Supports light/dark theme via Streamlit config.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/email-extractor.git
   cd email-extractor
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR engine (required for OCR support):

   - **Windows:**
     Download the installer from [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) or directly from [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki).
     Run the installer and follow the setup instructions.
     Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system PATH environment variable.

   - **macOS:**
     ```
     brew install tesseract
     ```

   - **Linux (Debian/Ubuntu):**
     ```
     sudo apt-get install tesseract-ocr
     ```

4. Verify Tesseract installation by running:
   ```
   tesseract --version
   ```

## Usage

Run the app locally:
```
streamlit run app.py
```

Upload files or enter URLs to extract emails. Use the "Start URL Scraping" button to begin recursive URL email extraction.

## Deployment

Deploy on Streamlit Cloud by connecting your GitHub repo.

## Tech Stack

- Streamlit
- PyMuPDF
- pandas
- email-validator
- pytesseract
- python-docx
- requests
- beautifulsoup4

## License

MIT License
