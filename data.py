
import requests
from bs4 import BeautifulSoup
import pandas as pd


url = "https://results.eci.gov.in/"

response = requests.get(url)
if response.status_code == 200:
    print("Successfully fetched the page!")
    soup = BeautifulSoup(response.content, 'html.parser')
    



