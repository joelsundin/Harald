import requests
from datetime import date

api_url = lambda date, api_key: f"https://api.worldnewsapi.com/search-news?language=sv&earliest-publish-date={date}&api-key={api_key}"

def fetch_news():
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable not set")
    today = str(date.today())
    response = requests.get(api_url(today, api_key))
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()