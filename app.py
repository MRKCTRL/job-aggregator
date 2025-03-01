from flask import Flask, render_template, request
import requests

app=Flask(__name__)


INDEED_API_KEY = ""
LINKEDIN_API_KEY = ""

INDEED_API_URL = ""
LINKEDIN_API_URL = ""


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


@app("/", methods=["GET", "POST"])
def index():
    jobs = []
    if request.method == "POST":
        keyword = request.form.get("keyword")
        location = request.form.get("location")
        
        
        indeed_jobs = fetch_indeed_jobs(keyword, location)
        linkedin_jobs = fetch_linkedin_jobs(keyword, location)
        
        
        jobs = indeed_jobs + linkedin_jobs 
        
        
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.main(debug=True)
