import os

class Config:

    def get_config():
        
        ai = {
            "model": os.getenv("OPENAI_MODEL"),
            "api_key": os.getenv("OPENAI_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL")
        }

        pdf = {
            "path": os.getenv("PDF_PATH"),
        }

        captcha = {
            "in_base_url": os.getenv("SOLVE_CAPTCHA_IN_URL"),
            "res_base_url": os.getenv("SOLVE_CAPTCHA_RES_URL"),
            "api_key": os.getenv("SOLVE_CAPTCHA_KEY"),
            "browser_agent": os.getenv("BROWSER_AGENT")
        }

        proxy = {
            "server": os.getenv("PROXY_SERVER"),
            "username":os.getenv("PROXY_USERNAME"),
            "password":os.getenv("PROXY_PASSWORD")
        }

        return {
            "ai": ai,
            "pdf": pdf,
            "captcha": captcha,
            "proxy": proxy
        }