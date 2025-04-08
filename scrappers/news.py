import requests
from bs4 import BeautifulSoup

def get_article_links(section="education", page=1):
    url = f"https://indianexpress.com/section/{section}/page/{page}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    articles = soup.select("div.title a")
    links = [a['href'] for a in articles if "http" in a['href']]
    return links

def scrape_article(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)
    date = soup.find("meta", {"property": "article:published_time"})['content']
    paragraphs = soup.select("div.full-details p")
    content = " ".join([p.get_text(strip=True) for p in paragraphs])

    return {
        "title": title,
        "url": url,
        "date": date,
        "content": content,
        "source": "Indian Express"
    }

import pandas as pd
import time

def scrape_section(section="education", max_pages=5):
    all_articles = []

    for page in range(1, max_pages+1):
        print(f"Scraping page {page}")
        links = get_article_links(section, page)
        for link in links:
            try:
                article = scrape_article(link)
                all_articles.append(article)
                time.sleep(1)  # Be polite
            except:
                continue

    df = pd.DataFrame(all_articles)
    df.to_csv(f"data/indianexpress_{section}.csv", index=False)

scrape_section()