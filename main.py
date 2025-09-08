from pdfextractor import PdfExtractor
from jobapplicationbot import JobApplicationBot

def main():
    """"
    Extracting PDF Content
    Constructing dictionary result for mapping Summary data
    """
    # print("Extracting PDF Content ...")
    # pdfextractor = PdfExtractor("docs/Kenneth.pdf")
    # pdfcontent = pdfextractor.extractPdf()    
    url = "https://jobs.workable.com/view/nh3yzcd2jraDf2Ki7Gj2y7/customer-service-engineer-(system-administrator)-(esom)-in-lexington-at-kentro"
    
    bot = JobApplicationBot(url, False)
    formFields = bot.getRequiredFields()
    
    for form in formFields:
        print(form, "\n")

if __name__ == "__main__":
    main()