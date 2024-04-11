import requests
from flask import Flask, render_template_string
from lxml import etree
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def get_departures():
    evaNo = 8000152  # Hannover Hbf EVANo
    date = datetime.now().strftime("%y%m%d")  # Aktuelles Datum ohne Bindestriche
    hour = datetime.now().strftime("%H")  # Aktuelle Stunde

    url = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/{evaNo}/{date}/{hour}"
    headers = {
        "DB-Client-Id": "f95a5e78f37597ae19ffb2d84a93f1f6",
        "DB-Api-Key": "61ab0e3bf7d3b47bf835decc65ee4f4c",
        "Accept": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        return f"Fehler beim API-Aufruf: {error_message}", 500

    if response.status_code == 200:
        try:
            root = etree.fromstring(response.content)
            departures = []

            for s in root.xpath('.//s'):
                for dp in s.xpath('.//dp'):
                    if dp.attrib.get('pp') == 'Hannover Hbf':
                        train = dp.xpath('.//tl')
                        if train:
                            train_name = train[0].attrib.get('n')
                            train_destination = dp.attrib.get('ppth')
                            scheduled_departure = train[0].attrib.get('pt')
                            platform = dp.attrib.get('pp')
                            departure_info = {
                                'train': train_name,
                                'destination': train_destination,
                                'scheduledDeparture': scheduled_departure,
                                'platform': platform
                            }
                            departures.append(departure_info)
        except Exception as e:
            return f"Fehler beim Parsen der API-Antwort: {str(e)}", 500

        return render_template_string(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Abfahrten</title>
                <style>
                    table {
                        border-collapse: collapse;
                        width: 100%;
                    }
                    th, td {
                        border: 1px solid black;
                        padding: 8px;
                        text-align: left;
                    }
                </style>
            </head>
            <body>
                <h1>Abfahrten von Hannover Hbf</h1>
                <table>
                    <tr>
                        <th>Zug</th>
                        <th>Ziel</th>
                        <th>Geplante Abfahrt</th>
                        <th>Gleis</th>
                    </tr>
                    {% for departure in departures %}
                    <tr>
                        <td>{{ departure.train }}</td>
                        <td>{{ departure.destination }}</td>
                        <td>{{ departure.scheduledDeparture }}</td>
                        <td>{{ departure.platform }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>
            """,
            departures=departures
        )

if __name__ == '__main__':
    app.run(debug=True)
