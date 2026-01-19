import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
job_listings = []
all_offers = []
page_number = 1
while True:
    print(f"Scraping page {page_number}...")
    URL = f'https://www.google.com/about/careers/applications/jobs/results/?distance=50&q=internship&page={page_number}'
    driver.get(URL)
    time.sleep(1) 

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    offers = soup.find_all('li', class_='lLd3Je')

    if not offers:
        print("No more jobs found. Stopping.")
        break
        
    all_offers.extend(offers)
    page_number += 1

    # stop if dispalyed page are less than full page
    if len(offers) < 20: 
        break

for idx, offer in enumerate(all_offers, start=0):
    job_el = offer.find(
        'a',
        class_='WpHeLc VfPpkd-mRLv6 VfPpkd-RLmnJb'
    )

    prefix_to_remove = "Learn more about "
    title = job_el.get('aria-label')
    cleaned_title = title.removeprefix(prefix_to_remove)

    relative_link = job_el.get('href')
    base_url = "https://www.google.com/about/careers/applications/"
    full_link = base_url + relative_link

    location = 'Unknown'
    location_span_wrapper = offer.find('span', class_='pwO9Dc vo5qdf')
    if location_span_wrapper:
        location_span = location_span_wrapper.find('span', class_='r0wTof')
        if location_span:
            location = location_span.text.strip()
            
    print(f"[{idx}/{len(all_offers)}] Scraping: {cleaned_title}, location: {location}")
    job_listings.append({
        "company": "Google",
        "job_title": cleaned_title,
        "job_link": full_link,
        "location": location
    })

driver.quit()

if job_listings:
    df = pd.DataFrame(job_listings)
    print(df.head())
    df.to_csv("google_internships.csv", index=False)
    print("\nSuccessfully saved job data to 'google_internships.csv'")
else:
    print("No job listings were scraped.")