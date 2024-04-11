from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_website():
    URL = "https://www.hannover.de/Service/Mobil-in-Hannover/Aktuelle-Verkehrshinweise"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all <div> elements with the specified class
    div_elements = soup.find_all('div', class_='col-md-12 col-lg-8 interesting-single__content')

    articles = []

    # Loop through each <div> element and extract its contents
    for div in div_elements:
        category = div.find('span', class_='ezstring-field').text.strip()
        title = div.find('h2', class_='interesting-single__title').text.strip()

        # Replace unwanted entities with an empty string in description
        description_tag = div.find('div', class_='interesting-single__description')
        description = description_tag.get_text().strip().replace('&shy;', '')  # Remove unwanted entities

        read_more_link = div.find('a', class_='content__read-more')['href'] if div.find('a', class_='content__read-more') else '#'
        likes_count_tag = div.find('p', class_='metadata__likes-count')
        likes_count = likes_count_tag.text.strip().split()[0] if likes_count_tag else 'N/A'  # Extract likes count or set to 'N/A' if not found


        article = {
            'category': category,
            'title': title,
            'description': description,
            'read_more_link': read_more_link,
            'likes_count': likes_count
        }

        articles.append(article)

    return articles

@app.route('/')
def home():
    articles = scrape_website()[:3]  # Display only the latest 3 articles
    
    # Generate homepage HTML
    homepage_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Homepage</title>
        <style>
            .main-container {
                width: 80%;
                margin: auto;
            }
            .article-container {
                border: 1px solid black;
                background-color: rgba(211, 211, 211, 0.5);
                padding: 10px;
                margin-bottom: 10px;
            }
            .navigation {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Homepage</h1>
        <div class="main-container">
    """
    for article in articles:
        homepage_html += f"""
            <div class="article-container">
                <h2>{article['title']}</h2>
                <p>Category: {article['category']}</p>
                <p>{article['description']}</p>
                <a href="{article['read_more_link']}" target="_blank">Mehr</a>
            </div>
        """
    homepage_html += """
        </div>
        <div class="navigation">
            <a href="/more_articles">Weitere Artikel anzeigen</a>
        </div>
    </body>
    </html>
    """

    return homepage_html

@app.route('/more_articles')
def more_articles():
    articles = scrape_website()[3:]  # Exclude the first 3 articles
    
    # Generate HTML for additional articles
    additional_articles_html = ""
    for article in articles:
        additional_articles_html += f"""
            <div class="article-container">
                <h2>{article['title']}</h2>
                <p>Category: {article['category']}</p>
                <p>{article['description']}</p>
                <a href="{article['read_more_link']}" target="_blank">Mehr</a>
            </div>
        """
    
    # Generate HTML for the entire page
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weitere Artikel</title>
        <style>
            .main-container {{
                width: 80%;
                margin: auto;
            }}
            .article-container {{
                border: 1px solid black;
                background-color: rgba(211, 211, 211, 0.5);
                padding: 10px;
                margin-bottom: 10px;
            }}
            .navigation {{
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Weitere Artikel</h1>
        <div class="main-container">
            {additional_articles_html}
        </div>
        <div class="navigation">
            <a href="/">Zurück zur Startseite</a>
        </div>
    </body>
    </html>
    """
    
    return page_html

if __name__ == '__main__':
    app.run(debug=True)
