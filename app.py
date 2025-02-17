from flask import Flask, render_template
import pymongo
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://deepika8383:Harekrishna@cluster0.5m1rpme.mongodb.net/")
db = client["newsDB"]
collection = db["tech_news"]

def scrape_and_store():
    URL = "https://techcrunch.com/"
    response = requests.get(URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = []

        articles = soup.find_all("a", class_="loop-card__title-link")

        for article in articles:
            title = article.get_text(strip=True)
            link = article["href"]
            timestamp = datetime.now(timezone.utc)  # Timezone-aware datetime

            # Check if the news already exists
            if not collection.find_one({"title": title}):
                news_list.append({"title": title, "link": link, "timestamp": timestamp})

        # Store in MongoDB
        if news_list:
            collection.insert_many(news_list)
            print(f"{len(news_list)} new articles stored successfully!")
        else:
            print("No new articles found!")

    else:
        print("Failed to fetch news")

def clean_old_news():
    # Delete articles older than 3 days
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
    result = collection.delete_many({"timestamp": {"$lt": three_days_ago}})
    print(f"Deleted {result.deleted_count} old articles.")

@app.route("/")
def home():
    # Run cleaning and scraping before rendering the page
    clean_old_news()
    scrape_and_store()
    
    # Fetch fresh news from MongoDB
    news = list(collection.find({}, {"_id": 0}))  
    return render_template("index.html", news=news)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's dynamic port
    app.run(host='0.0.0.0', port=port, debug=True)

