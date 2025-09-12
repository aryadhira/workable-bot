from playwright.sync_api import Page
import random
import time

class Util:

    @staticmethod
    def filling_mimic_human(page:Page, selector:str, value:str):        
        for i in value:
            page.keyboard.press(i)
            delay = random.uniform(0.05, 0.2)  
            time.sleep(delay)