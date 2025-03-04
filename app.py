from flask import Flask, render_template, request, flash, escape, make_response
from flask_wtf import FlaskForm
from wtfforms import StringField, validators
import requests

from math import ceil 

import re

from dotenv import load_dotenv
import os

import time


import logging



logging.basicConfig(
    level=logging(level=logging.INFO,
                  format="%(asctime)s - %(levelname)s - %(message)s",
                  handlers=[
                      logging.FIleHandler("app.log"),
                      logging.StreamHandler()
                  ]
)



load_dotenv()


app=Flask(__name__)
app.secret_key = os.get("")


INDEED_API_KEY = os.getenv("")
LINKEDIN_API_KEY = os.getenv("")
GLASSDOOR_API_KEY=os.getenv("")
GLASSDOOR_PARTNER_ID=""


INDEED_API_URL = ""
LINKEDIN_API_URL = ""
GLASSDOOR_API_URL=""

JOBS_PER_PAGE= 10

class JobSearchForm(FlaskForm):
    keyword= StringField("Keyword", [validators.InputRequired(), validators.Regexp(r"^[a-zA-Z0-9\s]+$")])
    loation = StringField("Location", [validators.InputRequired(), validators.Regexp(r"^[a-zA-Z\s,]+$")])


        

def fetch_indeed_jobs(keyword, location):
    time.sleep(1)
    try:
        params= {
            "publisher":INDEED_API_KEY ,
            "q": keyword ,
            "l": location,
            "format":"json",
                "v":"2" ,    
        }
        response = requests.get(INDEED_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching jobs from Indeed: {str(e)}")
        flash(f"Error fetching jons from Indeed: {str(e)}", "error")
        # if response.status_code == 200:
            # return response.json().get("results", [])
        return []


def fetch_linkedin_jobs(keyword, location):
    time.sleep(1)
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
    time.sleep(1)
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


def filter_jobs(jobs, job_type, min_salary):
    filtered_jobs=[]
    for job in jobs:
        if job_type and job.get("job_type") != job_type:
            continue
        if min_salary and job.get("salary", 0) < min_salary:
            continue
        filtered_jobs.append(job)
    return filtered_jobs

@app("/", methods=["GET", "POST"])
def index():
    form= JobSearchForm()
    jobs = []
    page = requests.args.get("page", 1, type=int)
    if form.validate_on_submit():
        # still need to do thios.
        keyword = sanitaze_input(form.keyword.data)
        location = sanitaze_input(form.loation.data)
        job=fetch_indeed_jobs + fetch_linkedin_jobs + fetch_glassdoor_jobs(keyword, location)
        
    if request.method == "POST":
        keyword = request.form.get("keyword").strip()
        location = request.form.get("location").strip()
        job_type=request.form.get("job_type")
        min_salary=request.form.get("min_salary", type=float)
        
        if not keyword or not location:
            flash("please enter both a keyword and location", "error")
        else:
            indeed_jobs = fetch_indeed_jobs(keyword, location)
            linkedin_jobs = fetch_linkedin_jobs(keyword, location)
            glassdoor_jobs = fetch_glassdoor_jobs(keyword, location)
            
            jobs = indeed_jobs + linkedin_jobs + glassdoor_jobs
            jobs= filter_jobs(jobs, job_type, min_salary)
            
            if not jobs: 
                flash("no jobs found. Try a different search.", "info")
            
        if not validate_keyword(keyword):
            flash("invalid keyword. Only aplhanumeric characters and spaces are allowed", "error")
        elif not validate_location(location):
            flash("invalid loation. Only letters, spaces and commas are allowed.", "error")
        else: 
            keyword = sanitaze_input(keyword)
            location = sanitaze_input(location)
        
        
        
        
        jobs = indeed_jobs + linkedin_jobs + glassdoor_jobs
        jobs= filter_jobs(jobs, job_type, min_salary)
        
    
    total_jobs = len(jobs)
    total_pages = ceil(total_jobs / JOBS_PER_PAGE)
    # start = (page - 1) * JOBS_PER_PAGE
    # end = start + JOBS_PER_PAGE 
    # jobs_to_display=jobs[start:end]  
    
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
        
        start = (page - 1) * JOBS_PER_PAGE
        end =start + JOBS_PER_PAGE
        jobs_to_display = job[start:end]
        
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