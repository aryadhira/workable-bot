from playwright.sync_api import Playwright
from playwright_stealth import stealth
from bs4 import BeautifulSoup
import time
import os
import re
import logging
from utils.utils import Util
import random

logger = logging.getLogger(__name__)

class JobBot:

    def __init__(self, pw, headless, resume, llm, config, pdf_path):
        self.resume = resume
        self.llm = llm
        self.headless = headless
        summary_content_raw = ""
        for key,value in self.resume.items():
            summary_content_raw += f"{key}: {value}\n"
        self.raw_summary = summary_content_raw
        self.playwright = pw
        self.config = config
        self.pdf_path = pdf_path
    
    def get_phone_dropdown(self, source):
        soup = BeautifulSoup(source, 'html.parser')

        country_code = soup.findAll("li", attrs={'data-country-code': True})
        phone_code = {}
        for li in country_code:
            phone_code[li.get('data-dial-code')] = li.get('data-country-code')

        return phone_code

    def get_required_field(self,source):
        soup = BeautifulSoup(source, 'html.parser')
        required_indicators = soup.find_all('strong', class_='styles__strong--2kqW6', string='*')

        required_fields = []

        for field in required_indicators:
            parent_container = field.parent.parent
            label = parent_container.next_element.next_sibling.find("strong").text.strip()

            form_container = parent_container.next_sibling
            input_selector = form_container.find(['input', 'textarea', 'select', 'fieldset', 'checkbox'])

            input_type = input_selector.get("type")
            dropdown_selector = None
            radio_options = []
            checkbox_options = []

            selector = None
            if input_selector.get('id'):
                selector = f"#{input_selector['id']}"
            elif input_selector.get('data-ui'):
                selector = f"[data-ui='{input_selector['data-ui']}']"
            elif input_selector.get('name'):
                selector = f"[name='{input_selector['name']}']"

            match input_type:
                case "text":
                    if input_selector.get("role") == "combobox":
                        input_type = "dropdown"
                        dropdown_selector = f"#{input_selector.get('aria-owns')}"
                    if input_selector.get("rows"):
                        input_type = "textarea"
                case "radio":
                    radio_input_name = input_selector.get("name")
                    selector = f"[data-ui='{radio_input_name}']"
                    option_selector = soup.find_all("input",{"name":radio_input_name})
                    for i in option_selector:
                        option_value = i.parent.parent.text.replace("SVGs not supported by this browser.", "")
                        radio_options.append(option_value.strip())
                case "checkbox":
                    checkbox_root = input_selector.parent.parent.parent
                    option_values_raw = checkbox_root.text.replace("SVGs not supported by this browser.", "-")
                    option_values = option_values_raw.split("---")
                    for opt in option_values:
                        if opt != "":
                            checkbox_options.append(opt)
            field_obj = {
                "label": label,
                "input_type": input_type,
                "selector": selector,
                "dropdown_selector": dropdown_selector,
                "radio_options": radio_options,
                "checkbox_options": checkbox_options
            }
            required_fields.append(field_obj)
        
        return required_fields
    
    def apply_job(self, url):
        proxy = {
            "server": self.config["proxy"]["server"],
            "username": self.config["proxy"]["username"],
            "password": self.config["proxy"]["password"]
        }

        browser_agent = self.config["captcha"]["browser_agent"]

        browser = self.playwright.start().chromium.launch(
            headless = self.headless,
            # slow_mo= 1000,
            # proxy= proxy
        )

        random_delay = random.uniform(2000,4000)

        try:
            context = browser.new_context(user_agent=browser_agent)
            page = context.new_page()

            stealth.Stealth().apply_stealth_async(page)
            
            logger.info(f'Navigating to {url} ...')
            page.goto(url)

            logger.info("Declining cookies ...")
            page.locator("button[data-ui='cookie-consent-accept']").click()

            page_root_source = page.content()

            logger.info("Navigating to Job Application Form ...")
            page.locator("button[data-ui='overview-apply-now']").click()

            form_dialog_container = page.locator("div[class='applicationForm__container--n_6Of']")
            form_dialog_container.wait_for(state='visible')
            logger.info("Waiting Form to Load ...")
            page.wait_for_timeout(5000)
            form_dialog_source = form_dialog_container.inner_html()

            logger.info("Populating All Required Fields ...")
            required_form_fields = self.get_required_field(form_dialog_source)
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, 200)

            for i in range(len(required_form_fields)):
                page.wait_for_timeout(random_delay)
                label = required_form_fields[i]["label"]
                selector = required_form_fields[i]["selector"]
                input_type = required_form_fields[i]["input_type"]

                if input_type == "text":
                    logger.info(f"filling {label} ...")

                    value = ""
                    if "?" in label:
                        value = self.llm.answer_question(label, input_type, "", self.raw_summary)
                    else:
                        value = self.resume[label]
                    page.locator(f"input{selector}").click()
                    Util.filling_mimic_human(page, f"input{selector}", value)

                elif input_type == "email":
                    logger.info(f"filling {label} ...")
                    value = self.resume[label]
                    page.locator(f"input{selector}").click()
                    Util.filling_mimic_human(page, f"input{selector}", value)

                elif input_type == "textarea":
                    logger.info(f"filling {label} ...")
                    value = "N/A"
                    page.locator(f"textarea{selector}").click()
                    Util.filling_mimic_human(page, f"textarea{selector}", value)

                elif input_type == "file":
                    logger.info(f"Uploading {label} ...")
                    page.set_input_files(selector, self.pdf_path)
                    page.wait_for_timeout(5000)

                elif input_type == "dropdown":
                    logger.info(f"Selecting {label} ...")
                    page.locator(f"input{selector}").click()
                    dropdown_selector = required_form_fields[i]["dropdown_selector"]
                    page.locator(f"{dropdown_selector}").wait_for(state="visible")
                    labelText = "Public Trust"
                    option_selector = page.get_by_role('option', name=labelText)
                    option_selector.click()

                elif input_type == "tel":
                    logger.info(f"Filling {label} ...")
                    value = self.resume[label]
                    phone_parts = value.split(" ")
                    dial_code = phone_parts[0]
                    phone_number = phone_parts[1]
                    phone_value = ""
                    dial_code = dial_code.replace("(","")
                    dial_code = dial_code.replace(")","")
                    dial_code_list = self.get_phone_dropdown(form_dialog_source)
                    country_code = ""
                    try:
                        country_code = dial_code_list[dial_code]
                    except KeyError:
                        logger.info("Dial Phone Code Not Found")

                    page.locator("div[class='iti__selected-flag']").click()
                    if country_code != "":
                        page.locator(f'li#iti-0__item-{country_code}').click()
                        phone_value = phone_number
                    else:
                        # dummy number if country code not found
                        page.locator('li#iti-0__item-us').click()
                        phone_value = "212-555-0125"
                    
                    page.locator(f"input{selector}").click()
                    Util.filling_mimic_human(page, f"input{selector}", phone_value)

                elif input_type == "checkbox":
                    logger.info(f"Answering: {label}")
                    page.locator(f"input{selector}").click()

                elif input_type == "radio":
                    logger.info(f"Answering: {label}")
                    radio_options = required_form_fields[i]["radio_options"]
                    str_options = "\n".join(radio_options)
                    answer = self.llm.answer_question(label, input_type, str_options, self.raw_summary)
                    option_selector_name = f"{label} {answer}"
                    fieldset_selector = f"fieldset{selector}"
                    page.locator(fieldset_selector).get_by_role("radio", name=option_selector_name).click()

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            page.locator("button[data-ui='apply-button']").click()

            page.wait_for_timeout(15000)


            
        except RuntimeError as e:
            logger.error(f"error applying job application: {e}")
