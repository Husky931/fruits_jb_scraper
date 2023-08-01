import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
import time
import random
from dotenv import load_dotenv
import os
import argparse
import re
import logging

# load environment variables
load_dotenv()

parser = argparse.ArgumentParser(description='Web scraping script.')
parser.add_argument('--country', required=True)
args = parser.parse_args()

url = f'http://pickingjobs.com/{args.country}'

log_file = f'logs/{args.country}_log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_sec_ch_ua(user_agent):
    browser_info = re.search(r"(Chrome|Firefox|Safari)/(\d+\.\d+)", user_agent['agent'])
    if browser_info is None:
        return "\"Not A Brand\";v=\"99\""
    else:
        brand, version = browser_info.groups()
        return f"\"{brand}\";v=\"{version}\", \" Not A Brand\";v=\"99\""
    
user_agents = [
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'platform': "\"macOS\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0', 'platform': "\"macOS\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A', 'platform': "\"macOS\""},
    {'agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36', 'platform': "\"Windows\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15', 'platform': "\"macOS\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36', 'platform': "\"macOS\""},
    {'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15', 'platform': "\"macOS\""}
]

selected_agent = random.choice(user_agents)
sec_ch_ua = generate_sec_ch_ua(selected_agent)

headers = {
    'Accept': '*/*',
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,mk;q=0.8,hr;q=0.7",
    'Connection': 'keep-alive',
    "Sec-Ch-Ua": sec_ch_ua,
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": selected_agent['platform'],
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": selected_agent['agent'],
    'Pragma': 'no-cache',  # HTTP 1.0.
    'Expires': '0',  # Proxies.
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

# Check if '#google_vignette' content exists in the response
if "google_vignette" in response.text:
    # If it does, sleep for a while (optional), then retry
    print("Detected ad overlay, refreshing...")
    time.sleep(random.uniform(1.0, 3.0))  # Random sleep between 1 and 3 seconds
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

job_posts = soup.find_all('span', class_='job-title')

# Establish a connection to your PostgreSQL database

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

# Create a cursor from the connection
cur = conn.cursor()

for post in job_posts:
    parent = post.parent

    job_title = post.text.strip()
    job_link = post.find('a')['href']

    company_tag = parent.find('span', class_='company')
    company = company_tag.text.strip() if company_tag else None

    location_tag = parent.find('span', class_='location')
    location = location_tag.text.strip() if location_tag else None

    description_tag = parent.find('span', class_='snippet')
    description = description_tag.text.strip() if description_tag else None

    time_posted_tag = parent.find('span', class_='time')
    time_posted = time_posted_tag.text.strip() if time_posted_tag else None

    try:
        cur.execute(
            """
            INSERT INTO job_posts (title, company_name, location, description, posted_date, url, country)
            VALUES  (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (title, description) DO NOTHING
            """,
            (job_title, company, location, description, time_posted, job_link, args.country)
        )

        # Commit the transaction
        conn.commit()

        if cur.rowcount:
            print(f'Job Title: {job_title} added to the database.')
            logging.info(f'Job Title: {job_title} added to the database.')
        else:
            print(f'Job Title: {job_title} already existed in the database.')
            logging.info(f'Job Title: {job_title} already existed in the database.')

    except Error as e:
        print(f'Failed to add Job Title: {job_title} to the database. Error: {str(e)}')
        logging.error(f'Failed to add Job Title: {job_title} to the database. Error: {str(e)}')

# Close the cursor and the connection
cur.close()
conn.close()

print('Finished processing job posts.')
