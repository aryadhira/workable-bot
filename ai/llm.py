from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class Llm:

    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.client = client
    
    def answer_question(self, question, input_type, options, summary):
        sys_message = ""

        if input_type == "radio":
            sys_message = f"""
                # ROLE
                Your role is to be Answer bot.
                
                ## TASK
                Your task is answering any question to fill any job application form that user ask to you.
                
                ## HOW TO ANSWER QUESTION
                When you get question from the user, you will find and refer the question from this Summary : 
                {summary}

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
        elif input_type == "text":
            sys_message = f"""
                # ROLE
                Your role is to be Answer bot.
                
                ## TASK
                Your task is answering any question to fill any job application form that user ask to you.
                
                ## HOW TO ANSWER QUESTION
                When you get question from the user, you will find and refer the question from this Summary : 
                {summary}

                ## OUTPUT
                Your output will be based on the question, if the question is Yes No question your output will only Yes or No, if the question is not Yes or No question you will answer only in short statement or few words only based on the Summary above.  

                ## ADDITIONAL INFORMATION
                - if the question is related with expected salary, answer it $4K/month
                - if the question is related with crime you will answer N/A, because no crime record
                - if the question is related visa status, answer it U.S Citizen / Green Card Holder
            """
        
        user_message = f'{question}?'

        messages = [
            {"role": "system", "content": sys_message},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"error calling LLM: {e}")
