
import re
import requests
from bs4 import BeautifulSoup

url = 'https://megogo.net/ua/collection/recently_added_movies_ua'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'lxml')

ad = ()

ad = soup.find_all('div', class_='card videoItem orientation-portrait size-normal')
ad = soup.find_all('div', class_='card-content video-content')
ad = soup.find_all('h3', class_='video-title card-content-title')

print(ad)
