from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright
from config.config import Config
from metadata.pdf import PdfMetadata
from core.job_bot import JobBot
from ai.llm import Llm
import logging

logging.basicConfig(level=logging.INFO)


def main():
    load_dotenv()
    cfg = Config.get_config()

    llm = Llm(
        api_key=cfg["ai"]["api_key"],
        base_url=cfg["ai"]["base_url"],
        model=cfg["ai"]["model"]
    )

    pdf_path = cfg["pdf"]["path"]
    metadata = PdfMetadata(pdf_path)
    resume = metadata.get_pdf_content()
    pw = sync_playwright().start()

    bot = JobBot(pw, False, resume, llm, cfg, pdf_path)

    urls = [
        "https://jobs.workable.com/view/nh3yzcd2jraDf2Ki7Gj2y7/customer-service-engineer-(system-administrator)-(esom)-in-lexington-at-kentro",
        "https://jobs.workable.com/view/6WYWj7iSEUTdgMfJERMvTF/selling-assistant-manager-in-greensboro-at-1915-south-%2F-ashley",
        "https://jobs.workable.com/view/xi5U92QV4yBxjaHrwLZYcF/hybrid-senior-technical-lead---front-end-in-texas-at-qode"
    ]

    for url in urls:
        bot.apply_job(url)

if __name__ == "__main__":
    main()