import streamlit as st
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_text_from_url,
    extract_emails,
    export_emails_to_csv,
    export_emails_to_txt,
    extract_emails_from_url_recursive,
)
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Email Extractor from Multiple Sources", layout="centered")

def main():
    st.image("assets/logo.png", width=150)
    st.title("Email Extractor from Multiple Sources")
    st.markdown(
        """
        Upload PDF, DOCX, or TXT files, or enter URLs to extract, validate, and export email addresses.
        Supports multiple file uploads and URL inputs with advanced validation and export options (.csv and .txt).
        """
    )

    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    url_input = st.text_area(
        "Or enter one or more URLs (one per line) to scrape emails from web pages",
        height=100,
    )

    start_scrape = st.button("Start URL Scraping")

    if not uploaded_files and not url_input.strip():
        st.warning("Please upload files or enter URLs to extract emails.")
        return

    all_emails = set()
    file_email_map = {}

    # Process uploaded files
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(uploaded_file)
            elif uploaded_file.type == "text/plain":
                text = extract_text_from_txt(uploaded_file)
            else:
                st.warning(f"Unsupported file type: {uploaded_file.type} for file {uploaded_file.name}")
                continue

            emails = extract_emails(text)
            file_email_map[uploaded_file.name] = emails
            all_emails.update(emails)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
            file_email_map[uploaded_file.name] = []

    # Process URLs
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]
    if start_scrape and urls:
        progress_bar = st.progress(0)
        total_urls = len(urls)
        for idx, url in enumerate(urls):
            try:
                emails = extract_emails_from_url_recursive(url)
                emails = sorted(emails)
                file_email_map[url] = emails
                all_emails.update(emails)
            except Exception as e:
                st.error(f"Error processing URL {url}: {e}")
                file_email_map[url] = []
            progress_bar.progress((idx + 1) / total_urls)
        progress_bar.empty()
    else:
        for url in urls:
            file_email_map[url] = []

    if not any(file_email_map.values()):
        st.warning("No valid emails found in the provided files or URLs.")
        return

    for source, emails in file_email_map.items():
        with st.expander(f"Emails found in {source} ({len(emails)})"):
            if emails:
                df = pd.DataFrame(emails, columns=["Email"])
                st.dataframe(df)
            else:
                st.info("No valid emails found in this source.")

    if all_emails:
        all_emails_sorted = sorted(all_emails)
        csv_data = export_emails_to_csv(all_emails_sorted)
        txt_data = export_emails_to_txt(all_emails_sorted)

        st.download_button(
            label="Download all emails as CSV",
            data=csv_data,
            file_name="emails.csv",
            mime="text/csv",
        )
        st.download_button(
            label="Download all emails as TXT",
            data=txt_data,
            file_name="emails.txt",
            mime="text/plain",
        )

    with st.sidebar:
        st.header("Help & Tips")
        st.markdown(
            """
            - Upload PDF, DOCX, or TXT files.
            - Or enter URLs (one per line) to scrape emails.
            - Emails are extracted using advanced validation.
            - Download combined emails as CSV or TXT.
            - For best results, upload clean files or valid URLs.
            - [GitHub Repo](https://github.com/yourusername/email-extractor)
            """
        )

if __name__ == "__main__":
    main()
