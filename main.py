from pdfextractor import PdfExtractor
from dotenv import load_dotenv
from openai import OpenAI
import os
from jobapplicationbot import JobApplicationBot
import time

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
    
    # url = "https://jobs.workable.com/view/nh3yzcd2jraDf2Ki7Gj2y7/customer-service-engineer-(system-administrator)-(esom)-in-lexington-at-kentro"

    url = "https://jobs.workable.com/view/6WYWj7iSEUTdgMfJERMvTF/selling-assistant-manager-in-greensboro-at-1915-south-%2F-ashley"

    # url = "https://jobs.workable.com/view/xi5U92QV4yBxjaHrwLZYcF/hybrid-senior-technical-lead---front-end-in-texas-at-qode"

    bot = JobApplicationBot(url, False, pdfcontent, llmClient)
    bot.fillForm()
    # bot.dumpSource("customerengineer.txt")
    # source = open("sellingassistant.txt", "r")
    # source = open("customerengineer.txt", "r")
    # source = open("frontendsenior.txt", "r")

    # bot.collectRequireField(source.read())

if __name__ == "__main__":
    main()