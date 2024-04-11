from flask import Flask
from flask import render_template
import datetime as dt
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

#commands
# conda activate env 
#   aktiviert die Umegbung, bei erstellung wurde env als name gwählt
# flask --app app run
#   Anwendung starten "app" ist der name der anwendung da app.py


app = Flask(__name__)
username = 'whiteholenetwork_wehowsky_stefan'
password = '20Emf65dBC'

@app.route('/')
def index():
    json_data = fetch_weather()
    current_wind, current_temp, current_precip = current_data(json_data)
    time_data, temperature_list, wind_list, precip_list = create_data_list(json_data)

    # Calculate the length of the first third
    third_length = len(time_data) // 3

    # Extract the temperature data for the first third
    first_third_temps = temperature_list[:third_length]

    # Find the maximum and minimum temperatures for the first third
    max_temp_first_third = max(first_third_temps)
    min_temp_first_third = min(first_third_temps)

     # Artikel von der Website abrufen
    articles = scrape_website()
    # Die aktuellsten drei Artikel auswählen
    latest_articles = articles[:10]
    # HTML für die Anzeige der Artikel innerhalb des Containers generieren
    articles_html = ""
    for article in latest_articles:
        articles_html += f"""
            <div class="article-container">
                <h3>{article['title']}</h3>
                <p><strong>Kategorie:</strong> {article['category']}</p>
                <p>{article['description']}</p>
                <a href="{article['read_more_link']}" target="_blank">Mehr</a>
            </div>
        """
    departure_time_html = read_from_file("fahrplan.txt")
    timestamp = read_from_file("last_query_timestamp.txt")

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href='https://fonts.googleapis.com/css?family=Workbench' rel='stylesheet'>
        <link href='https://fonts.googleapis.com/css?family=Oswald' rel='stylesheet'>
        <style>
            body {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: min-content 1fr 1fr 1fr;
            gap:2px;
            }}

            .WeatherContainer {{
                align-self: start;
                margin: auto; /* Zentrieren Sie das Element horizontal */
                background-color: #CDCFD9;
                font-family: 'Workbench';
                font-size: 1.05em; /* Verwenden Sie relative Schriftgröße */
                position: relative;
                width: 100%;
                height: 100%;
                overflow-y: hidden;
            }}
            .full-width-div {{
                width: 90%; /* Ändern Sie die Breite in Prozent */
                margin: auto; /* Zentrieren Sie das Element horizontal */
                height: 50vh; /* Ändern Sie die Höhe in Viewport-Höhe */
                background-color: lightblue;
                margin-bottom: 2vw; /* Verwenden Sie relative Einheiten für den Abstand */
                border: 2px solid black;
                overflow-y: auto;
            }}
            .WeatherMaxMin {{
                display: flex;
                justify-content: space-around; 
                
            }}
            #weatherChart {{
                margin-bottom: 5px;
            }}
            .WeatherValues {{
                display: flex;
                justify-content: space-around;
            }}
            .WeatherValues div {{
                width: 30%;
            }}
            .container-head {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2vw; /* Verwenden Sie relative Einheiten für den Abstand */
                height: 5vh; /* Ändern Sie die Höhe in Viewport-Höhe */
            }}
            canvas {{
                width: auto;
                height: auto;
            }}
            #sunIcon, #umbrellaIcon {{
                display: none;
                position: absolute;
                top: 10px;
                right: 10px;
            }}
            #jacketIcon, #pulloverIcon, #tshirtIcon {{
                display: none;
                position: absolute;
                top: 10px;
                left: 10px;
            }}

             .article-container {{
                border: 1px solid black;
                background-color: rgba(211, 211, 211, 0.5);
                font-family: Oswald;
                margin-top: 2px;
                margin-left: 2px;
                margin-right: 2px
                padding: 5px;
            }}
            /* CSS für Tabellen */
            table {{
                font-family: Oswald;
                font-size: 1.05em;
                width: 100%;
                border-collapse: collapse;
                border-spacing: 0;
                margin-bottom: 20px;
                font-family: Arial, sans-serif;
            }}

            table th, table td {{
                font-size: 1.05em;
                font-family: Oswald;
                padding: 8px;
                border: 1px solid #dddddd;
                text-align: left;
            }}

            table th {{
                font-family: Oswald;
                background-color: #f2f2f2;
            }}

            table tr:nth-child(even) {{
                font-family: Oswald;
                background-color: #f9f9f9;
            }}

            table tr:hover {{
                background-color: #f2f2f2;
            }}
            .timestamp-box {{
            font-family: Oswald;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            padding: 10px;
            margin-top: 20px; /* Hier kannst du den Abstand nach Bedarf anpassen */
            text-align: right; /* Um den Text rechtsbündig anzuzeigen */
            font-style: italic; /* Optional: Kursivschrift verwenden */
            }}

        </style>
    </head>
    <body>
    <div class="full-width-div">
    <div class="WeatherContainer">
    <div class="container-head">
        <div>
            <img src="../static/sun.png" id="sunIcon" alt="Sun Icon" width="50">
            <img src="../static/umberella.png" id="umbrellaIcon" alt="Umbrella Icon" width="50">
            <img src="../static/jacket.png" id="jacketIcon" alt="Jacket Icon" width="50">
            <img src="../static/pullover.png" id="pulloverIcon" alt="Pullover Icon" width="50">
            <img src="../static/tshirt.png" id="tshirtIcon" alt="T-Shirt Icon" width="50">
        </div>
        <div>
            <p align="center">Wetter Hannover</p>
        </div>
        <div>
        </div>
    </div>
        <canvas id="weatherChart"></canvas>
        <div class="WeatherValues">
            <div>
                <p>Temperatur: {current_temp} °C</p>
            </div>
            <div>
                <p>Wind: {current_wind} m/s</p>
            </div>
            <div>
                <p>Regen: {current_precip} mm</p>
            </div>
        </div>
        <div class="WeatherMaxMin"> 
            <div>
                <p> Temp. Max (24h): {max_temp_first_third} °C </p>
            </div>
            <div>
                <p> Temp. Min (24h): {min_temp_first_third} °C </p>
            </div>
        </div>
    </div>
    </div>
    <div class="full-width-div">
        <div id="article-list">
                {articles_html}
            </div>
    </div>
    <div class="full-width-div">
        <h2 style="font-family: 'Oswald'; text-align: center;">Bahn zur Uni</h2>
        {departure_time_html}
        <div class="timestamp-box">
            <p>Zuletzt aktualisiert: {timestamp}</p>
        </div>
    </div>

    <div class="full-width-div"></div>
    <div class="full-width-div"></div>
        <script>
            document.addEventListener('DOMContentLoaded', function () {{
                var ctx = document.getElementById('weatherChart').getContext('2d');

                var timeLabels = {time_data}; 
                var temperatureData = {temperature_list}; 
                var windData = {wind_list}; 
                var precipData = {precip_list}; 

                var myChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: timeLabels,
                        datasets: [{{
                            label: 'Temperatur',
                            data: temperatureData,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 3
                        }},
                        {{
                            label: 'Windgeschwindigkeit',
                            data: windData,
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 3
                        }},
                        {{
                            label: 'Niederschlag',
                            data: precipData,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 3
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }});
            document.addEventListener('DOMContentLoaded', function () {{
            var currentPrecip = {current_precip}; // Assuming current_precip contains the precipitation value
            var currentTemp = {current_temp};

            // Get the sun and umbrella icons
            var sunIcon = document.getElementById('sunIcon');
            var umbrellaIcon = document.getElementById('umbrellaIcon');
            var jacketIcon = document.getElementById('jacketIcon');
            var pulloverIcon = document.getElementById('pulloverIcon');
            var tshirtIcon = document.getElementById('tshirtIcon');

            // Show the appropriate icon based on the Temperature value
            if (currentTemp >= 15 && currentTemp <= 20) {{
                pulloverIcon.style.display = 'inline-block';
                tshirtIcon.style.display = 'none'; // Hide the others
                jacketIcon.style.display = 'none';
            }}
            else if (currentTemp > 20) {{
                tshirtIcon.style.display = 'inline-block'; 
                pulloverIcon.style.display = 'none'; // Hide the others
                jacketIcon.style.display = 'none';
            }} 
            else {{
                jacketIcon.style.display = 'inline-block';
                pulloverIcon.style.display = 'none'; // Hide the others
                tshirtIcon.style.display = 'none';
            }}

                // Show the appropriate icon based on the precipitation value
                if (currentPrecip < 0.1) {{
                    sunIcon.style.display = 'inline-block';
                }} else {{
                    umbrellaIcon.style.display = 'inline-block';
                }}
            }});
        </script>
    </body>
    </html>
    """

def fetch_weather():
    startdate = dt.datetime.now().replace(minute=0, second=0, microsecond=0)
    enddate = startdate + dt.timedelta(days=3)
    startdate_str = startdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    enddate_str = enddate.strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f'https://{username}:{password}@api.meteomatics.com/{startdate_str}--{enddate_str}:PT1H/t_2m:C,precip_1h:mm,wind_speed_10m:ms/52.37502,09.73322/json'
    response = requests.get(url)
    json_data = response.json()
    if response.status_code == 200:
        return json_data
    else:
        print('Fehler bei der API-Anfrage:', response.status_code)
        return None

def create_data_list(json_data):
    time_data = []
    temperature_list = []
    wind_list = []
    precip_list = []

    for entry in json_data.get('data', []):
        if entry.get('parameter') == 't_2m:C':
            temperature_data = entry.get('coordinates', [])[0].get('dates', [])
            for data in temperature_data:
                time_data.append(data.get('date', 'N/A').replace('2024-', '').replace('T',' | ').replace(':00Z','')) 
                temperature_list.append(data.get('value', None))
        elif entry.get('parameter') == 'wind_speed_10m:ms':
            wind_data = entry.get('coordinates', [])[0].get('dates', [])
            for data in wind_data:
                wind_list.append(data.get('value', None))
        elif entry.get('parameter') == 'precip_1h:mm':
            precip_data = entry.get('coordinates', [])[0].get('dates', [])
            for data in precip_data:
                precip_list.append(data.get('value', None))

    return time_data, temperature_list, wind_list, precip_list

def current_data(json_data):
    current_temp = None
    current_wind = None
    current_precip = None

    for entry in json_data.get('data', []):
        if entry.get('parameter') == 't_2m:C':
            current_temp = entry.get('coordinates', [])[0].get('dates', [])[0].get('value')
        elif entry.get('parameter') == 'wind_speed_10m:ms':
            current_wind = entry.get('coordinates', [])[0].get('dates', [])[0].get('value')
        elif entry.get('parameter') == 'precip_1h:mm':
            current_precip = entry.get('coordinates', [])[0].get('dates', [])[0].get('value')
    return current_wind, current_temp, current_precip
    
def scrape_website():
    base_url = "https://www.hannover.de"
    URL = base_url + "/Service/Mobil-in-Hannover/Aktuelle-Verkehrshinweise"
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
        description = description_tag.get_text().strip().replace('&shy;', '').replace('lesen', '')  # Remove unwanted entities

        read_more_link = base_url + (div.find('a', class_='content__read-more')['href'] if div.find('a', class_='content__read-more') else '#')

        article = {
            'category': category,
            'title': title,
            'description': description,
            'read_more_link': read_more_link,
        }

        articles.append(article)

    return articles

def read_from_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == '__main__':
    app.run()