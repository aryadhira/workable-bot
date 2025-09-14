from playwright.sync_api import Page
import random
import time

class Util:

    @staticmethod
    def filling_mimic_human(page:Page, selector:str, value:str):       
        page.locator(selector).fill("") 
        for i in value:
            page.keyboard.type(i)
            delay = random.uniform(0.04, 0.3)  
            time.sleep(delay)