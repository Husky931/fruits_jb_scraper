from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import psycopg2
from psycopg2 import Error
import time
import random
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import argparse

# load environment variables
load_dotenv()

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

parser = argparse.ArgumentParser(description='Web scraping script.')
parser.add_argument('--country', required=True)
args = parser.parse_args()

# Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
random_user_agent = random.choice(user_agents)
chrome_options.add_argument(f'user-agent={random_user_agent}')

# Initiate webdriver
print("Starting WebDriver...\n")
driver = webdriver.Chrome(service=Service('path-to-chromedriver'), options=chrome_options)

url = f'http://pickingjobs.com/{args.country}'
print(f"Navigating to {url}...\n")
driver.get(url)

# Wait up to 10 seconds for the page to load
wait = WebDriverWait(driver, 10)

try:
    # Wait until the google_vignette ad appears
    wait.until(EC.presence_of_element_located((By.ID, 'ad_position_box')))

    # Perform click outside of the ad to close it
    size = driver.get_window_size()
    action = ActionChains(driver)
    action.move_by_offset(size['width'] - 10, 15).click().perform()
    # action.move_by_offset(5, 5)  
    action.click()
    action.perform()

    # Alternatively, you can simulate pressing ESC key to close the ad
    # action.send_keys(Keys.ESCAPE)
    # action.perform()

    time.sleep(3)

except TimeoutException:
    print("Ad did not appear within the wait time.\n")

# After handling the ad, proceed with your scraping
soup = BeautifulSoup(driver.page_source, 'html.parser')

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
        else:
            print(f'Job Title: {job_title} already existed in the database.')

    except Error as e:
        print(f'Failed to add Job Title: {job_title} to the database. Error: {str(e)}')

# Close the cursor and the connection
cur.close()
conn.close()

print('Finished processing job posts.')

# Don't forget to close the driver at the end
driver.quit()
