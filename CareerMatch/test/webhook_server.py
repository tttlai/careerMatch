from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import process_jobs
import uvicorn
from typing import Optional

app = FastAPI()

class JobRequest(BaseModel):
    user_id: str
    job_url: str

@app.post("/trigger-job-search")
async def trigger_job_search(request: JobRequest):
    try:
        print(f"Received request for user_id: {request.user_id}")
        print(f"Processing job URL: {request.job_url}")
        
        # Process jobs with the provided user_id and URL
        result = await process_jobs(request.user_id, request.job_url)
        
        return {
            "status": "success",
            "message": "Jobs processed successfully",
            "processed_jobs": len(result) if result else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 