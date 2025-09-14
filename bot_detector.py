from playwright.sync_api import sync_playwright
from config.config import Config
from dotenv import load_dotenv

def run():
    load_dotenv()
    cfg = Config.get_config()
    proxy = {
        "server": cfg["proxy"]["server"],
        "username":cfg["proxy"]["username"],
        "password": cfg["proxy"]["password"]
    }
    pw = sync_playwright().start()

    browser = pw.chromium.launch(
        headless=False,
        proxy=proxy
    )

    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        storage_state="state.json",
    )

    context.add_init_script("""
        delete Object.getPrototypeOf(navigator).webdriver;
    """)
    
    page = context.new_page()

    page.goto("https://www.browserscan.net/bot-detection")


    page.pause()

if __name__ == "__main__":
    run()