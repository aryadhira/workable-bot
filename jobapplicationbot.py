from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class JobApplicationBot:
    def __init__(self, url, headless):
        self.url = url
        # self.playwright = sync_playwright().start()
        # self.browser = self.playwright.chromium.launch(
        #     headless=headless,
        #     slow_mo=2000
        # )

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

        

    def getRequiredFields(self):
        sourceFile = open("source.txt", "r")
        source = sourceFile.read()

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
            
            formField = {
                "Label" : requiredLabelText,
                "InputType": inputType,
                "InputElement": inputElement
            }

            requireFormFields.append(formField)

        return requireFormFields
            



        