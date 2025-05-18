from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime

class SupabaseOperations:
    def __init__(self):
        load_dotenv()
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_API_KEY')
        )

    async def insert_job_data(self, analyzed_data, job_url, user_id):
        try:
            job_entry = {
                "created_at": datetime.utcnow().isoformat(),
                "Salary": analyzed_data.get("Salary", ""),
                "Location": analyzed_data.get("Location", ""),
                "Company": analyzed_data.get("Company", ""),
                "Position": analyzed_data.get("Position", ""),
                "Job Posting Title": analyzed_data.get("Job posting title", ""),
                "link": job_url,
                "published_date": "",
                # "user_id": user_id,  # Use the provided user_id
                "match_score": 0.8
            }

            result = self.supabase.table('jobs_n8n').insert(job_entry).execute()
            print(f"Inserted job for user {user_id}: {job_entry['Job Posting Title']}")
            return result.data
        except Exception as e:
            print(f"Error inserting into Supabase: {str(e)}")
            return None 