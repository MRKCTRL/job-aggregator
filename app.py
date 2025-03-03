from flask import Flask, render_template, request, flash, escape, make_response
from flask_wtf import FlaskForm
from wtfforms import StringField, validators
import requests
from math import ceil 
import re

app=Flask(__name__)
app.secret_key = ""

INDEED_API_KEY = ""
LINKEDIN_API_KEY = ""

INDEED_API_URL = ""
LINKEDIN_API_URL = ""

GLASSDOOR_API_KEY=""
GLASSDOOR_PARTNER_ID=""
GLASSDOOR_API_URL=""

JOBS_PER_PAGE= 10

class JobSearchForm(FlaskForm):
    keyword= StringField("Keyword", [validators.InputRequired(), validators.Regexp(r"^[a-zA-Z0-9\s]+$")])
    loation = StringField("Location", [validators.InputRequired(), validators.Regexp(r"^[a-zA-Z\s,]+$")])


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

def sanitaze_input(input_string):
    return escape(input_string)


def validate_keyword(keyword):
    return bool(re.match(r"^[a-zA_Z0-9\s]+$", keyword))


def validate_location(location):
    return bool(re.match(r"^[a-zA-Z\s,]+$", location))



@app("/", methods=["GET", "POST"])
def index():
    form= JobSearchForm()
    jobs = []
    page = requests.args.get("page", 1, type=int)
    if form.validate_on_submit():
        # still need to do thios.
        keyword = sanitaze_input(form.keyword.data)
        location = sanitaze_input(form.loation.data)
        jobs=fetch_indeed_jobs + fetch_linkedin_jobs + fetch_glassdoor_jobs(keyword, location)
        
    if request.method == "POST":
        keyword = request.form.get("keyword").strip()
        location = request.form.get("location").strip()
        
        if not validate_keyword(keyword):
            flash("invalid keyword. Only aplhanumeric characters and spaces are allowed", "error")
        elif not validate_location(location):
            flash("invalid loation. Only letters, spaces and commas are allowed.", "error")
        else: 
            keyword = sanitaze_input(keyword)
            location = sanitaze_input(location)
        
        
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

@app.after_request
def add_csp_header(response):
    csp_header = (
        "default-src 'self' ;"
        "script-src 'self' https://trusted.cdn.com; "
        "style-src 'self' https://trusted.cdn.com; "
        "img-src 'self' https://trusted.cdn.com; "
        "object-src 'none';"
    )
    response.headers["Content-Secruity-Policy"] = csp_header 
    return response

if __name__ == "__main__":
    app.main(debug=True)
