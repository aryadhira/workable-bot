from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import os

class JobApplicationBot:
    def __init__(self, url, headless, resume, llm):
        self.url = url
        self.resume = resume
        self.llm = llm
        summaryContentRaw = ""
        for key,value in self.resume.items():
            summaryContentRaw += f"{key}: {value}\n"
        
        self.rawSummary = summaryContentRaw
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            slow_mo=2000
        )
    
    # For scrapping on dev purpose only
    def dumpSource(self, name):
        page = self.browser.new_page()
        print(f'Navigating to {self.url} ...')
        page.goto(self.url)

        print("Handling cookies ...")
        page.locator("button[data-ui='cookie-consent-decline']").click()

        print("Navigating to Job Application Form ...")
        page.locator("button[data-ui='overview-apply-now']").click()

        dialogContainer = page.locator("div[class='applicationForm__container--n_6Of']")
        dialogContainer.wait_for(state='visible')
        print("Waiting Form to Load ...")
        time.sleep(5)
        dialogHtml = dialogContainer.inner_html()
        with open(name, "w",encoding="utf-8") as file:
            file.write(dialogHtml)
    
    def getPhoneDropdown(self, source):
        soup = BeautifulSoup(source, 'html.parser')

        countryCode = soup.findAll("li", attrs={'data-country-code': True})
        phoneCode = {}
        for li in countryCode:
            phoneCode[li.get('data-dial-code')] = li.get('data-country-code')

        return phoneCode

    def answeringFormQuestion(self, question, inputType, options):
        model = os.getenv("OPENAI_MODEL")
        sysMessage = ""
        if inputType == "radio":
            sysMessage = f"""
                # ROLE
                Your role is to be Answer bot.
                
                ## TASK
                Your task is answering any question to fill any job application form that user ask to you.
                
                ## HOW TO ANSWER QUESTION
                When you get question from the user, you will find and refer the question from this Summary : 
                {self.rawSummary}

                ## ADDITIONAL INFORMATION
                - if the question is related with expected salary, answer it $4K/month
                - if the question is related with crime you will answer N/A
                - if the question is related visa status, answer it U.S Citizen / Green Card Holder

                ## OUTPUT
                Since this is radio button question, Your output will be only one of list below:
                {options}

                ## ANSWERING RULE
                - If you found the question related with the summary, you will answer it based on that reference.
                - If you can't find any reference from the summary, just pick one of the list above
            """
        elif inputType == "text":
            sysMessage = f"""
                # ROLE
                Your role is to be Answer bot.
                
                ## TASK
                Your task is answering any question to fill any job application form that user ask to you.
                
                ## HOW TO ANSWER QUESTION
                When you get question from the user, you will find and refer the question from this Summary : 
                {self.rawSummary}

                ## OUTPUT
                Your output will be based on the question, if the question is Yes No question your output will only Yes or No, if the question is not Yes or No question you will answer only in short statement or few words only based on the Summary above.  

                ## ADDITIONAL INFORMATION
                - if the question is related with expected salary, answer it $4K/month
                - if the question is related with crime you will answer N/A, because no crime record
                - if the question is related visa status, answer it U.S Citizen / Green Card Holder
            """

        userMessage = f'{question}?'

        messages = [
            {"role": "system", "content": sysMessage},
            {"role": "user", "content": userMessage},
        ]
        try:
            response = self.llm.chat.completions.create(
                model=model,
                messages=messages
            )

            return response.choices[0].message.content
        except Exception as e:
            return e
        
    def collectRequireField(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        requiredIndicators = soup.find_all('strong', class_='styles__strong--2kqW6', string='*')

        requireFields = []

        for field in requiredIndicators:
            parentContainer = field.parent.parent
            label = parentContainer.next_element.next_sibling.find("strong").text.strip()
            formContainer = parentContainer.next_sibling
            inputSelector = formContainer.find(['input', 'textarea', 'select', 'fieldset', 'checkbox'])

            inputType = inputSelector.get("type")
            dropdownSelector = None
            radioOptions = []
            checkboxOptions = []

            selector = None
            if inputSelector.get('id'):
                selector = f"#{inputSelector['id']}"
            elif inputSelector.get('data-ui'):
                selector = f"[data-ui='{inputSelector['data-ui']}']"
            elif inputSelector.get('name'):
                selector = f"[name='{inputSelector['name']}']"

            match inputType:
                case "text":
                    if inputSelector.get("role") == "combobox":
                        inputType = "dropdown"
                        dropdownSelector = f"#{inputSelector.get('aria-owns')}"
                    if inputSelector.get("rows"):
                        inputType = "textarea"
                case "radio":
                    radioInputName = inputSelector.get("name")
                    selector = f"[data-ui='{radioInputName}']"
                    optionSelector = soup.find_all("input",{"name":radioInputName})
                    for i in optionSelector:
                        optionValue = i.parent.parent.text.replace("SVGs not supported by this browser.", "")
                        radioOptions.append(optionValue.strip())
                case "checkbox":
                    checkboxRoot = inputSelector.parent.parent.parent
                    optionValuesRaw = checkboxRoot.text.replace("SVGs not supported by this browser.", "-")
                    optionValues = optionValuesRaw.split("---")
                    for opt in optionValues:
                        if opt != "":
                            checkboxOptions.append(opt)

            fieldObj = {
                "label": label,
                "inputType": inputType,
                "selector": selector,
                "dropdownSelector": dropdownSelector,
                "radioOptions": radioOptions,
                "checkboxOptions": checkboxOptions
            }
            requireFields.append(fieldObj)
        
        return requireFields
    
    def fillForm(self):
        try:
            page = self.browser.new_page()
            print(f'Navigating to {self.url} ...')
            page.goto(self.url)

            print("Handling cookies ...")
            page.locator("button[data-ui='cookie-consent-decline']").click()

            print("Navigating to Job Application Form ...")
            page.locator("button[data-ui='overview-apply-now']").click()

            dialogContainer = page.locator("div[class='applicationForm__container--n_6Of']")
            dialogContainer.wait_for(state='visible')
            print("Waiting Form to Load ...")
            time.sleep(5)
            dialogHtml = dialogContainer.inner_html()

            print("Populating All Required Fields ...")
            formFields = self.collectRequireField(dialogHtml)
            time.sleep(1)

            for i in range(len(formFields)):
                label = formFields[i]["label"]
                selector = formFields[i]["selector"]
                inputType = formFields[i]["inputType"]

                if inputType == "text" or inputType == "email":
                    print(f"Filling {label} ...")
                    value = ""
                    if "?" in label:
                        value = self.answeringFormQuestion(label,inputType,"")  
                    else:
                        value = self.resume[label]
                    
                    formLocation = page.locator(f"input{selector}")
                    formLocation.fill(value)
                elif inputType == "textarea":
                    print(f"Filling {label} ...")
                    formLocation = page.locator(f"textarea{selector}")
                    formLocation.fill("N/A")
                elif inputType == "file":
                    print(f"Uploading {label} ...")
                    page.set_input_files(selector, os.getenv("PDF_PATH"))
                    page.wait_for_timeout(2000)
                elif inputType == "dropdown":
                    print(f"Selecting {label} ...")
                    page.locator(f"input{selector}").click()
                    dropdownSelector = formFields[i]["dropdownSelector"]
                    page.locator(f"{dropdownSelector}").wait_for(state="visible")
                    labelText = "Public Trust"
                    optionSelector = page.get_by_role('option', name=labelText)
                    optionSelector.click()
                elif inputType == "tel":
                    print(f"Filling {label} ...")
                    value = self.resume[label]
                    phoneParts = value.split(" ")
                    dialCode = phoneParts[0]
                    phoneNumber = phoneParts[1]
                    phoneValue = ""
                    dialCode = dialCode.replace("(","")
                    dialCode = dialCode.replace(")","")
                    dialCodeList = self.getPhoneDropdown(dialogHtml)
                    countryCode = ""
                    try:
                        countryCode = dialCodeList[dialCode]
                    except KeyError:
                        print("Dial Phone Code Not Found")

                    page.locator("div[class='iti__selected-flag']").click()
                    if countryCode != "":
                        page.locator(f'li#iti-0__item-{countryCode}').click()
                        phoneValue = phoneNumber
                    else:
                        # dummy number if country code not found
                        page.locator('li#iti-0__item-us').click()
                        phoneValue = "212-555-0123"
                        
                    formLocation = page.locator(f"input{selector}")
                    formLocation.fill(phoneValue)
                elif inputType == "radio":
                    print(f"Answering: {label}")
                    radioOptions = formFields[i]["radioOptions"]
                    strOptions = "\n".join(radioOptions)
                    answer = self.answeringFormQuestion(label,inputType,strOptions)
                    optionSelectorName = f"{label} {answer}"
                    fieldsetSelector = f"fieldset{selector}"
                    page.locator(fieldsetSelector).get_by_role("radio", name=optionSelectorName).click()
                    time.sleep(1)
                elif inputType == "checkbox":
                    print(f"Answering: {label}")
                    page.locator(f"input{selector}").click()


        except RuntimeError as e:
            print(f"Failed to fill the form: {e}")
                    
                    



            



        