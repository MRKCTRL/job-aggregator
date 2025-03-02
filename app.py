from flask import Flask, render_template, request
import requests
from math import ceil 


app=Flask(__name__)


INDEED_API_KEY = ""
LINKEDIN_API_KEY = ""

INDEED_API_URL = ""
LINKEDIN_API_URL = ""

GLASSDOOR_API_KEY=""
GLASSDOOR_PARTNER_ID=""
GLASSDOOR_API_URL=""

JOBS_PER_PAGE= 10



def fetch_indeed_jobs(keyword, location):
    params= {
        "publisher":INDEED_API_KEY ,
        "q": keyword ,
        "l": location,
        "format":"json",
         "v":"2" ,    
    }
    response = requests.get(INDEED_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def fetch_linkedin_jobs(keyword, location):
    headers = {
        "Authorization" : f"Bearer{LINKEDIN_API_KEY}"
    } 
    params = {
        "keywords": keyword,
        "location": location
    }
    response = requests.get(LINKEDIN_API_KEY, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("elements", [])
    return []

def fetch_glassdoor_jobs(keyword, location):
    params = {
        "v": "1",
        "t.p" : GLASSDOOR_PARTNER_ID,
        "t.k" : GLASSDOOR_API_KEY,
        "action" : "jobs",
        "q" : keyword,
        "l" : location 
    }
    response = requests.get(GLASSDOOR_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("response", {}).get("jobs", [])
    return []


@app("/", methods=["GET", "POST"])
def index():
    jobs = []
    page = requests.args.get("page", 1, type=int)
    if request.method == "POST":
        keyword = request.form.get("keyword")
        location = request.form.get("location")
        
        
        indeed_jobs = fetch_indeed_jobs(keyword, location)
        linkedin_jobs = fetch_linkedin_jobs(keyword, location)
        glassdoor_jobs = fetch_glassdoor_jobs(keyword, location)
        
        
        jobs = indeed_jobs + linkedin_jobs + glassdoor_jobs
        
    
    total_jobs = len(jobs)
    total_pages = ceil(total_jobs / JOBS_PER_PAGE)
    start = (page - 1) * JOBS_PER_PAGE
    end = start + JOBS_PER_PAGE 
    jobs_to_display=jobs[start:end]  
        
    return render_template("index.html", jobs=jobs_to_display, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.main(debug=True)
