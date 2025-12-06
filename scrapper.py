import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://careers.google.com/jobs/results/?distance=50&q=internship'

print("Initializing browser driver automatically...")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.get(URL)

try:
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(3) 

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

except Exception as e:
    print(f"An error occurred during scrolling: {e}")

html = driver.page_source
driver.quit() 

soup = BeautifulSoup(html, 'html.parser')

job_listings = []

job_elements = soup.find_all('a', class_='WpHeLc VfPpkd-mRLv6 VfPpkd-RLmnJb') 

for job_el in job_elements:
    
    prefix_to_remove = "Learn more about "
    title = job_el.get('aria-label')

    cleaned_title = title.removeprefix(prefix_to_remove)

    relative_link = job_el.get('href')
    base_url = "https://www.google.com/about/careers/applications/"
    full_link = base_url + relative_link

    job_listings.append({
        'job_title': cleaned_title,
        'job_link': full_link
    })


if job_listings:
    df = pd.DataFrame(job_listings)

    print(df.head())

    df.to_csv('google_internships.csv', index=False)
    print("\n Successfully saved job data to 'google_internships.csv'")
else:
    print(" No job listings were scraped.")