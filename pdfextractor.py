import pdfplumber
import re

class PdfExtractor:
    def __init__(self, path):
        self.path = path

    def extractPdf(self):
        try:
            content = ""
            biodata = ""
            with pdfplumber.open(self.path) as pdf:
                firstPage = pdf.pages[0]
                biodata = firstPage.extract_text_lines()
                
                for page in pdf.pages:
                    text = page.extract_text()
                    content += text
            nameSection = biodata[0]['text']
            identity = biodata[1]['text']
            identityParts = identity.split("|")
    
            summarySection = self.findSection(content,"PROFESSIONAL SUMMARY")
            technicalSection = self.findSection(content,"TECHNICAL SKILLS")
            experienceSection = self.findSection(content,"EXPERIENCE")
            educationSection = self.findSection(content,"EDUCATION")
            projectSection = self.findSection(content,"PROJECTS & HACKATHONS")
            certificationsSection = self.findSection(content,"CERTIFICATIONS")

            pdfContent = {
                "Name": nameSection,
                "Address": identityParts[0].strip(),
                "Email": identityParts[1].strip(),
                "Phone": identityParts[2].strip(),
                "Summary": summarySection,
                "Skill": technicalSection,
                "Experience": experienceSection,
                "Education": educationSection,
                "Project": projectSection,
                "Certification": certificationsSection
            }

            return pdfContent
        except Exception as e:
            print(f'Error Extract PDF: {e}')

    def findSection(self, text, sectionName, nextSection=["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "EXPERIENCE", "EDUCATION", "PROJECTS & HACKATHONS", "CERTIFICATIONS"]):
        pattern = re.compile(rf"{sectionName}[\n]?")
        match = pattern.search(text)
        if not match:
            return ""

        start = match.end()

        end = len(text)
        for ns in nextSection:
            nsPattern = re.compile(rf"{ns}[\n]?")
            nsMatch = nsPattern.search(text, start)
            if nsMatch:
                end = min(end, nsMatch.start())

        return text[start:end].strip()