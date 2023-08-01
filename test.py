import requests
import random
import json
import re

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

url = 'https://httpbin.org/post'

data = {
    "key": "value"
}

response = requests.post(url, headers=headers, json=data)

# The returned json includes a 'headers' field with all the headers that were received by httpbin.org
print(json.dumps(response.json()['headers'], indent=4))
