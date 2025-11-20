
import requests
from bs4 import BeautifulSoup

def fetch_website_contents(url: str) -> str:
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page. Status: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator="\n").strip()
