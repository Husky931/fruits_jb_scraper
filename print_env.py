# test_env.py
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# get environment variables
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

# print environment variables
print("DB_NAME:", dbname)
print("DB_USER:", user)
print("DB_PASSWORD:", password)
print("DB_HOST:", host)
print("DB_PORT:", port)

# yo