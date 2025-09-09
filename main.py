from pdfextractor import PdfExtractor
from jobapplicationbot import JobApplicationBot

def main():
    print("Extracting PDF Content ...")
    pdfextractor = PdfExtractor("docs/Kenneth.pdf")
    pdfcontent = pdfextractor.extractPdf()    
    
    url = "https://jobs.workable.com/view/nh3yzcd2jraDf2Ki7Gj2y7/customer-service-engineer-(system-administrator)-(esom)-in-lexington-at-kentro"
    
    bot = JobApplicationBot(url, False, pdfcontent)
    # source = open("source.txt", "r")
    # fields = bot.getRequiredFields(source)

    # for i in fields:
    #     print(i)
    bot.fillApplicationForm()


if __name__ == "__main__":
    main()