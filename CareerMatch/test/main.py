from linkedInExtractJobs import extract_jobs, process_job_urls
from job_analyzer import JobAnalyzer
from db_operations import SupabaseOperations
from dotenv import load_dotenv
import os
import json
import asyncio
import requests

async def process_single_url(url, base_url, analyzer, db_client, user_id):
    """Process a single URL through the entire pipeline immediately"""
    try:
        print(f"\nProcessing URL: {url}")
        
        # 1. Process the URL using process_job_urls logic
        payload = {"url": url}
        response = requests.post(base_url, json=payload)
        
        if response.status_code != 200:
            print(f"Failed to process URL: {url}")
            return None
            
        try:
            job_details = response.json()
            if isinstance(job_details, dict) and 'body' in job_details:
                job_details = json.loads(job_details['body'])
            print("URL processed successfully")
        except json.JSONDecodeError:
            print(f"Failed to parse response for URL: {url}")
            return None
        
        # 2. Immediately analyze with OpenAI
        print("Analyzing with OpenAI...")
        analyzed_data = analyzer.analyze_job_data(job_details)
        if not analyzed_data:
            print("OpenAI analysis failed")
            return None
        print("OpenAI analysis complete")
        
        # 3. Immediately store in Supabase with user_id
        print("Storing in Supabase...")
        await db_client.insert_job_data(analyzed_data, url, user_id)
        print(f"Successfully completed pipeline for: {analyzed_data.get('Job posting title', '')}")
        
        return analyzed_data
        
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return None

async def process_jobs(user_id: str, job_search_url: str):
    """Main processing function that can be called by webhook"""
    load_dotenv()
    
    try:
        # Initialize components
        analyzer = JobAnalyzer()
        db_client = SupabaseOperations()
        base_url = os.getenv('JOB_DETAILS_API_URL')
        
        if not base_url:
            raise ValueError("JOB_DETAILS_API_URL not set")
        
        # Get all URLs from extract_jobs
        print(f"Extracting job URLs for user {user_id}...")
        initial_result = extract_jobs(job_search_url)
        
        # Handle API Gateway response format
        if isinstance(initial_result, dict) and 'body' in initial_result:
            result = json.loads(initial_result['body'])
        else:
            result = initial_result
            
        all_urls = result.get('links', [])
        print(f"Found {len(all_urls)} URLs to process")
        
        # Process each URL through the entire pipeline immediately
        successful_jobs = []
        for i, url in enumerate(all_urls[:10], 1):
            print(f"\nStarting pipeline for job {i} of {len(all_urls)}")
            processed_job = await process_single_url(url, base_url, analyzer, db_client, user_id)
            if processed_job:
                successful_jobs.append(processed_job)
                print(f"Pipeline complete for job {i}")
            else:
                print(f"Pipeline failed for job {i}")
        
        print(f"\nFinal count - Successfully processed: {len(successful_jobs)} jobs")
        return successful_jobs
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    # For direct script execution, use default values
    asyncio.run(process_jobs(
        user_id="default_user",
        job_search_url=os.getenv('DEFAULT_JOB_SEARCH_URL', '')
    )) 