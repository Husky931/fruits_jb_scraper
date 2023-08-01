import requests
import json
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os
import random
import argparse

load_dotenv()

parser = argparse.ArgumentParser(description='Web scraping script.')
parser.add_argument('--country', required=True)
args = parser.parse_args()

url = "https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/it-IT?apikey=AE50QWejwK4J73X1y1uNqpWRr2PmKB3S"

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
]

headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,mk;q=0.8,hr;q=0.7",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.monster.it",
    "Referer": "https://www.monster.it/lavoro/cerca?q=Raccoglitrice+di+frutta&where=&page=1&so=m.h.s",
    "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": random.choice(user_agents),
}

payload = {
    "jobQuery": {
        "query": "Raccoglitrice di frutta",
        "locations": [
            {
                "country": "it",
                "address": "",
                "radius": {"unit": "km","value": 20}
            }
        ]
    },
    "jobAdsRequest": {
        "position": [1,2,3,4,5,6,7,8,9],
        "placement": {
            "channel": "MOBILE",
            "location": "JobSearchPage",
            "property": "monster.it",
            "type": "JOB_SEARCH",
            "view": "CARD"
        }
    },
    "fingerprintId": "z81d5d31455e5e9233db966d9826990f2",
    "offset": 9,
    "pageSize": 9,
    "histogramQueries": ["count(company_display_name)", "count(employment_type)"],
    "includeJobs": []
}

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code != 200:
    print(f"Error: Received status code {response.status_code} from the server.")
    # handle the error here...
    # For now, we'll just stop processing, you can add more sophisticated error handling if you want.
    exit(1)

data = response.json()
job_results = data.get('jobResults', [])

for job in job_results:
    job_posting = job.get('jobPosting', {})

    # description = job_posting.get('description', "N/A")[:200]
    description = job.get('enrichments', {}).get('processedDescriptions', {}).get('shortDescription', "N/A")
    url = job_posting.get('url', "N/A")
    date_posted = job_posting.get('datePosted', "N/A")
    title = job_posting.get('title', "N/A")
    company_name = job_posting.get('hiringOrganization', {}).get('name', "N/A")

    job_location = job_posting.get('jobLocation', [{}])
    if job_location:
        location = job_location[0].get('address', {}).get('addressLocality', "N/A")
    else:
        location = "N/A"

    try:
        cur.execute(
            """
            INSERT INTO job_posts (title, company_name, location, description, posted_date, url, country)
            VALUES  (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (title, description) DO NOTHING
            """,
            (title, company_name, location, description, date_posted, url, args.country)
        )

        conn.commit()

        if cur.rowcount:
            print(f'Job Title: {title} added to the database.')
        else:
            print(f'Job Title: {title} already existed in the database.')

    except Error as e:
        print(f'Failed to add Job Title: {title} to the database. Error: {str(e)}')

cur.close()
conn.close()

print('Finished processing job posts.')
