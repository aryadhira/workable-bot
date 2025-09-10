from pdfextractor import PdfExtractor
from dotenv import load_dotenv
from openai import OpenAI
import os
from jobapplicationbot import JobApplicationBot
from playwright.sync_api import sync_playwright


def main():
    load_dotenv()

    OPENAI_KEY = os.getenv("OPENAI_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

    llmClient = OpenAI(
        api_key=OPENAI_KEY,
        base_url=OPENAI_BASE_URL
    )

    print("Extracting PDF Content ...")
    pdfextractor = PdfExtractor("docs/Kenneth.pdf")
    pdfcontent = pdfextractor.extractPdf()    
    
    pw = sync_playwright().start()

    urls = [
        "https://jobs.workable.com/view/nh3yzcd2jraDf2Ki7Gj2y7/customer-service-engineer-(system-administrator)-(esom)-in-lexington-at-kentro",
        "https://jobs.workable.com/view/6WYWj7iSEUTdgMfJERMvTF/selling-assistant-manager-in-greensboro-at-1915-south-%2F-ashley",
        "https://jobs.workable.com/view/xi5U92QV4yBxjaHrwLZYcF/hybrid-senior-technical-lead---front-end-in-texas-at-qode"
    ]

    for url in urls:
        bot = JobApplicationBot(pw, url, False, pdfcontent, llmClient)
        bot.fillForm()


if __name__ == "__main__":
    main()