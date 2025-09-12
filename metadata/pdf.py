import pdfplumber
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PdfMetadata:
    
    def __init__(self, path):
        self.path = path

    def get_pdf_content(self):
        try:
            logger.info("extracting PDF ...")
            content = ""
            with pdfplumber.open(self.path) as pdf:
                first_page = pdf.pages[0]
                biodata = first_page.extract_text_lines()
                
                for page in pdf.pages:
                    text = page.extract_text()
                    content += text
            name_section = biodata[0]['text']
            name_parts = name_section.split(" ")
            first_name = name_parts[0]
            last_name = name_parts[1]
            identity = biodata[1]['text']
            identity_parts = identity.split("|")

            summary_section = self.find_section(content,"PROFESSIONAL SUMMARY")
            technical_section = self.find_section(content,"TECHNICAL SKILLS")
            experience_section = self.find_section(content,"EXPERIENCE")
            education_section = self.find_section(content,"EDUCATION")
            project_section = self.find_section(content,"PROJECTS & HACKATHONS")
            certification_section = self.find_section(content,"CERTIFICATIONS")
            join_time = datetime.now()+timedelta(days=7)
            join_time_str = join_time.strftime("%d %B, %Y")

            pdf_content = {
                "First name": first_name,
                "Last name": last_name,
                "Address": identity_parts[0].strip(),
                "Email": identity_parts[1].strip(),
                "Phone": identity_parts[2].strip(),
                "Summary": summary_section,
                "Skill": technical_section,
                "Experience": experience_section,
                "Education": education_section,
                "Project": project_section,
                "Certification": certification_section,
                "Available start date": join_time_str,
                "Current level of clearance": "Public Trust"
            }

            return pdf_content
        
        except Exception as e:
            logger.error(f"error extracting PDF: {e}")
    
    def find_section(self, text, section_name, next_section=["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "EXPERIENCE", "EDUCATION", "PROJECTS & HACKATHONS", "CERTIFICATIONS"]):
        pattern = re.compile(rf"{section_name}[\n]?")
        match = pattern.search(text)
        if not match:
            return ""

        start = match.end()

        end = len(text)
        for ns in next_section:
            nsPattern = re.compile(rf"{ns}[\n]?")
            nsMatch = nsPattern.search(text, start)
            if nsMatch:
                end = min(end, nsMatch.start())

        return text[start:end].strip()