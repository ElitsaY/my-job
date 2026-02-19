import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


def scrape_google_internships(driver):
    job_listings = []
    all_offers = []
    page_number = 1
    while True:
        print(f"Scraping Google page {page_number}...")
        url = (
            "https://www.google.com/about/careers/applications/jobs/results/"
            f"?target_level=INTERN_AND_APPRENTICE&page={page_number}"
        )
        driver.get(url)
        time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        offers = soup.find_all("li", class_="lLd3Je")

        if not offers:
            print("No more Google jobs found. Stopping.")
            break

        all_offers.extend(offers)
        page_number += 1

        # Stop if displayed page is less than a full page
        if len(offers) < 20:
            break

    for idx, offer in enumerate(all_offers, start=0):
        job_el = offer.find("a", class_="WpHeLc VfPpkd-mRLv6 VfPpkd-RLmnJb")
        if not job_el:
            continue

        prefix_to_remove = "Learn more about "
        title = job_el.get("aria-label") or ""
        cleaned_title = title.removeprefix(prefix_to_remove).strip()

        relative_link = job_el.get("href") or ""
        base_url = "https://www.google.com/about/careers/applications/"
        full_link = base_url + relative_link

        location = "Unknown"
        location_span_wrapper = offer.find("span", class_="pwO9Dc vo5qdf")
        if location_span_wrapper:
            location_span = location_span_wrapper.find("span", class_="r0wTof")
            if location_span:
                location = location_span.text.strip()

        print(f"[Google {idx}/{len(all_offers)}] {cleaned_title}, location: {location}")
        job_listings.append(
            {
                "company": "Google",
                "job_title": cleaned_title,
                "job_link": full_link,
                "location": location,
            }
        )

    return job_listings


def scrape_nvidia_workday(driver, url):
    job_listings = []
    print("Scraping NVIDIA Workday listings...")
    driver.get(url)
    time.sleep(2)

    # Try to expand all results if a "Load more" button exists
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        load_more = soup.find(attrs={"data-automation-id": "loadMoreButton"})
        if not load_more:
            break
        try:
            driver.execute_script("arguments[0].click();", driver.find_element("css selector", "[data-automation-id='loadMoreButton']"))
            time.sleep(1.5)
        except Exception:
            break

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Workday job cards commonly use data-automation-id attributes
    cards = soup.find_all(attrs={"data-automation-id": "jobSearchResult"})
    if not cards:
        # Fallback to any anchor that looks like a job detail link
        cards = soup.find_all("a", href=lambda h: h and "/en-US/NVIDIAExternalCareerSite/job/" in h)

    for idx, card in enumerate(cards, start=0):
        title = ""
        link = ""
        location = "Unknown"

        title_el = card.find(attrs={"data-automation-id": "jobTitle"})
        if title_el:
            title = title_el.get_text(strip=True)
            link = title_el.get("href") or ""
        else:
            # If card is already the anchor
            if card.name == "a":
                title = card.get_text(strip=True)
                link = card.get("href") or ""

        location_el = card.find(attrs={"data-automation-id": "locations"})
        
        if not location_el:
            location_el = card.find(attrs={"data-automation-id": "location"})
        if location_el:
            location = location_el.get_text(strip=True)

        # print(f"Location element: {location_el}")
        if not title or not link:
            continue

        if link.startswith("/"):
            link = "https://nvidia.wd5.myworkdayjobs.com" + link

        print(f"[NVIDIA {idx}/{len(cards)}] {title}, location: {location}")
        job_listings.append(
            {
                "company": "NVIDIA",
                "job_title": title,
                "job_link": link,
                "location": location,
            }
        )

    return job_listings


def merge_locations(job_listings):
    merged = {}
    order = []
    for job in job_listings:
        key = (job["company"], job["job_title"], job["job_link"])
        if key not in merged:
            merged[key] = {
                "company": job["company"],
                "job_title": job["job_title"],
                "job_link": job["job_link"],
                "location": [],
            }
            order.append(key)
        if job.get("location"):
            merged[key]["location"].append(job["location"])

    results = []
    for key in order:
        locations = merged[key]["location"]
        # Preserve order while de-duplicating
        seen = set()
        unique_locations = []
        for loc in locations:
            if loc not in seen:
                seen.add(loc)
                unique_locations.append(loc)
        merged[key]["location"] = ", ".join(unique_locations) if unique_locations else "Unknown"
        results.append(merged[key])
    return results


def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    job_listings = []
    job_listings.extend(scrape_google_internships(driver))
    job_listings.extend(
        scrape_nvidia_workday(
            driver,
            "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite"
            "?workerSubType=0c40f6bd1d8f10adf6dae42e46d44a17"
            "&locationHierarchy1=2fcb99c455831013ea52e9ef1a0032ba"
            "&locationHierarchy1=2fcb99c455831013ea52adc65f5d3254"
            "&locationHierarchy1=d21cf68980ad0121a67d319db107a200",
        )
    )

    driver.quit()

    if job_listings:
        job_listings = merge_locations(job_listings)
        df = pd.DataFrame(job_listings)

        df.to_csv("google_internships.csv", index=False)
        print("\nSuccessfully saved job data to 'google_internships.csv'")
    else:
        print("No job listings were scraped.")


main()