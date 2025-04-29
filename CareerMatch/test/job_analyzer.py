import os
import json
from openai import OpenAI
from dotenv import load_dotenv

class JobAnalyzer:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.system_prompt = """You are a job posting analyst who will extract usefull information from the given input.
        The required data:
        1. Salary
        2. Location
        3. Company
        4. Position
        5. Job posting title
        Return this in clean JSON format without any extra characters in the structure"""

    def analyze_job_data(self, job_data):
        try:
            job_content = job_data.get('content', '')
            if isinstance(job_content, dict):
                job_content = json.dumps(job_content)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": job_content}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error analyzing job data: {str(e)}")
            return None
