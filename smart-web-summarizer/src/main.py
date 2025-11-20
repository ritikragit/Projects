
from .fetcher import fetch_website_contents
from .summarize import summarize_text

def summarize_website(url: str):
    print(f"🔍 Fetching: {url}")
    text = fetch_website_contents(url)
    print("\n🤖 Summarizing...\n")
    print(summarize_text(text))

if __name__ == "__main__":
    summarize_website("https://xyz.com")
