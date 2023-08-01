import requests
import json
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os
import random
import re

load_dotenv()

url = "https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-GB?apikey=AE50QWejwK4J73X1y1uNqpWRr2PmKB3S"

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
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,mk;q=0.8,hr;q=0.7",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.monster.de",
    "Referer": "https://www.monster.de/jobs/suche?q=Obstpfl%C3%BCcker&where=&page=1&so=m.s.sh",
    "Sec-Ch-Ua": sec_ch_ua,
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": selected_agent['platform'],
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": selected_agent['agent']
}

payload = {
    "jobQuery": {
        "query": "Farm hand",
        "locations": [{
            "country": "gb",
            "address": "",
            "radius": {
                "unit": "mi",
                "value": 20
            }
        }]
    },
    "jobAdsRequest": {
        "position": [1,2,3,4,5,6,7,8,9],
        "placement": {
            "channel": "MOBILE",
            "location": "JobSearchPage",
            "property": "monster.co.uk",
            "type": "JOB_SEARCH",
            "view": "CARD"
        }
    },
    "fingerprintId": "z1b5bc05dbdff255ab22b5e626e040552",
    "offset": 18,
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
    country  = 'england'
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
            (title, company_name, location, description, date_posted, url, country)
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