import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

def get_required_env_var(var_name):
    """
    Get a required environment variable or raise an error if not found.
    
    Args:
        var_name (str): Name of the environment variable
        
    Returns:
        str: Value of the environment variable
        
    Raises:
        ValueError: If the environment variable is not set
    """
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Required environment variable {var_name} is not set in config.env")
    return value

def extract_jobs(job_url):
    """
    Extracts job listings from LinkedIn using the API Gateway endpoint.
    
    Args:
        job_url (str): The LinkedIn job search URL to scrape
        
    Returns:
        dict: The parsed JSON response from the API
    """
    # Get API URL from environment variables
    url = get_required_env_var('JOBS_API_URL')
    
    # Define the request payload
    payload = {
        "url": job_url
    }
    
    # Send the POST request
    response = requests.post(url, json=payload)
    
    # Try to parse and return the response
    try:
        return response.json()
    except ValueError:
        print("Error: Response is not valid JSON")
        return {"error": "Invalid JSON response", "raw_response": response.text}

def process_job_urls(jobs_response):
    """
    Processes each job URL from the extract_jobs response and makes additional API calls.
    
    Args:
        jobs_response (dict): The response from extract_jobs containing job URLs
        
    Returns:
        list: List of responses from processing each job URL
    """
    # Get API URL from environment variables
    base_url = get_required_env_var('JOB_DETAILS_API_URL')
    
    processed_responses = []
    
    # Check if the response contains job URLs
    if not isinstance(jobs_response, dict):
        print("Error: Invalid response format")
        return processed_responses
    
    # Get job links from response
    jobs = jobs_response.get('links', [])
    
    for job in jobs:
        print(job)   
        try:
            # Make API call for each job URL
            payload = {"url": job}
            response = requests.post(base_url, json=payload)
            
            # Process the response
            if response.status_code == 200:
                try:
                    job_details = response.json()
                    processed_responses.append(job_details)
                    print(f"\nProcessing job URL: {job}")
                    print("Response:")
                    print(json.dumps(job_details, indent=2))
                except ValueError:
                    print(f"Error: Invalid JSON response for URL: {job}")
            else:
                print(f"Error: API call failed for URL: {job}")
                print(f"Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing URL {job}: {str(e)}")
    
    return processed_responses

# if __name__ == "__main__":
#     try:
#         # Get default job search URL from environment variables
#         job_search_url = get_required_env_var('DEFAULT_JOB_SEARCH_URL')
#         result = extract_jobs(job_search_url)
        
#         # Print the first API call response in pretty JSON format
#         print("\nFirst API Call Response:")
#         print(json.dumps(result, indent=2))
        
#         # Process the job URLs
#         processed_results = process_job_urls(result)
        
#         print("\nTotal jobs processed:", len(processed_results))
#     except ValueError as e:
#         print(f"Configuration error: {str(e)}")
#         print("Please make sure config.env file exists and contains all required variables:")
#         print("- JOBS_API_URL")
#         print("- JOB_DETAILS_API_URL")
#         print("- DEFAULT_JOB_SEARCH_URL")
