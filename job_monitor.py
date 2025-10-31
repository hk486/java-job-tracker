import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

# --- Config ---
SEARCH_QUERY = "java developer 3 years"
JOB_BOARDS = {
    "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords=java%20developer%203%20years",
    "Indeed": "https://www.indeed.com/jobs?q=java+developer+3+years",
    "Naukri": "https://www.naukri.com/java-developer-3-years-jobs",
    "Glassdoor": "https://www.glassdoor.co.in/Job/java-developer-3-years-jobs-SRCH_KO0,25.htm",
    "Monster": "https://www.foundit.in/search?query=java%20developer%203%20years"
}

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
EMAIL_TO  = os.environ.get("EMAIL_TO")

# --- Location keywords for India ---
INDIA_LOCATIONS = [
    "india", "bangalore", "bengaluru", "mumbai", "delhi", "noida", "gurgaon", "hyderabad",
    "chennai", "pune", "kolkata", "ahmedabad", "coimbatore", "jaipur", "surat", "visakhapatnam",
    "bhubaneswar", "indore", "lucknow", "kanpur", "nagpur", "thiruvananthapuram", "kochi"
]

def is_india_job(text):
    text_lower = text.lower()
    return any(city in text_lower for city in INDIA_LOCATIONS)

# --- Fetch jobs from generic boards ---
def fetch_jobs():
    job_results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for source, url in JOB_BOARDS.items():
        try:
            print(f"🔍 Searching {source}...")
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "lxml")

            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]

                # Filter by relevant keyword
                if any(k in text.lower() for k in ["java", "backend", "developer", "engineer"]):
                    # Filter by location (India or Indian cities)
                    if is_india_job(text):
                        # Build absolute URL if relative
                        if not href.startswith("http"):
                            base = url.split("/jobs")[0]
                            href = base + href

                        job_results.append({
                            "title": text[:120],
                            "link": href,
                            "source": source
                        })
        except Exception as e:
            print(f"⚠️ Error fetching from {source}: {e}")

    # Remove duplicates
    unique = {job["link"]: job for job in job_results}
    return list(unique.values())

# --- LinkedIn Outreach Message ---
def outreach_message(title, source):
    return (
        f"I came across the '{title}' role on {source}, and it aligns well with my Java backend experience. "
        f"I’d appreciate the opportunity to discuss how I could contribute to this position."
    )

# --- Email Sender ---
def send_email(jobs):
    if not jobs:
        print("No new jobs found.")
        return

    body = f"🕐 Hourly Java Developer Job Updates ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    for j in jobs[:15]:
        body += f"• {j['title']}\n{j['link']}\n"
        body += f"LinkedIn message: {outreach_message(j['title'], j['source'])}\n\n"

    msg = MIMEText(body, "plain")
    msg["Subject"] = "Hourly Java Developer Job Updates"
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("✅ Email sent successfully!")

# --- Main ---
if __name__ == "__main__":
    print("🚀 Starting hourly job search...")
    jobs = fetch_jobs()
    print(f"Found {len(jobs)} jobs.")
    send_email(jobs)