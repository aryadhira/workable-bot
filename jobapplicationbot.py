from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class JobApplicationBot:
    def __init__(self, url, headless, resume):
        self.url = url
        self.resume = resume
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            slow_mo=3000
        )

    def fillApplicationForm(self):
        page = self.browser.new_page()
        print(f'Navigating to {self.url} ...')
        page.goto(self.url)

        print("Handling cookies ...")
        page.locator("button[data-ui='cookie-consent-decline']").click()

        print("Navigating to Job Application Form ...")
        page.locator("button[data-ui='overview-apply-now']").click()

        dialogContainer = page.locator("div[class='applicationForm__container--n_6Of']")
        dialogContainer.wait_for(state='visible')

        dialogHtml = dialogContainer.inner_html()

        print("Populating All Required Fields ...")
        formFields = self.getRequiredFields(dialogHtml)
        
        for i in range(len(formFields)):
            selector = formFields[i]["Selector"]
            if formFields[i]["InputType"] == "text" or formFields[i]["InputType"] == "email":
                label = formFields[i]["Label"]
                value = self.resume[label]
                formLocation = page.locator(f"input{selector}")
                formLocation.fill(value)
            elif formFields[i]["InputType"] == "file":
                page.set_input_files(selector, "docs/Kenneth.pdf")
                page.wait_for_timeout(2000)
        

    def getRequiredFields(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        requiredIndicators = soup.find_all('strong', class_='styles__strong--2kqW6', string='*')

        requireFormFields = []

        for required in requiredIndicators:
            requiredParent = required.parent.parent

            requiredLabel = requiredParent.next_element.next_sibling.find('strong')
            if not requiredLabel:
                continue

            requiredLabelText = requiredLabel.text.strip()

            formContainer = requiredParent.parent.parent
            inputElement = formContainer.find(['input', 'textarea', 'select', 'fieldset'])

            inputType = "unknown"
            if inputElement:
                match inputElement.name:
                    case 'input':
                        inputType = inputElement.get('type')
                    case 'fieldset':
                        if inputElement.find('input', type='radio'):
                            inputType = "radio"
                        elif inputElement.find('input', type='checkbox'):
                            inputType = "checkbox"
                    case _:
                        inputType = inputElement
            selector = None
            if inputElement.get('id'):
                selector = f"#{inputElement['id']}"
            elif inputElement.get('data-ui'):
                selector = f"[data-ui='{inputElement['data-ui']}']"
            elif inputElement.get('name'):
                selector = f"[name='{inputElement['name']}']"
            
            formField = {
                "Label" : requiredLabelText,
                "InputType": inputType,
                "Selector": selector,

            }

            requireFormFields.append(formField)

        return requireFormFields
    
    def getPhoneDropdown(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        dialCodeOptions = soup.find_all('span', class_='iti__dial-code')
        dialCodes = []

        for option in dialCodeOptions:
            dialCodes.append(option.text)

        return dialCodes    
    



        