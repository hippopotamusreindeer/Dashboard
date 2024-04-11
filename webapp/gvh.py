from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

def save_to_file(html_content, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

def scrape_connections():
    driver = webdriver.Edge()
    driver.get("https://www.gvh.de/fahrplan/auskunft/?context=TP")

    # Wartezeit für das Laden der Webseite
    time.sleep(10)  

    # Accept Cookies-Button
    cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ccm--decline-cookies.ccm--ctrl-init")))
    cookie_button.click()
    #print(cookie_button)

    # Warte auf das Laden des iframes
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.iframe")))

    # switch to selected iframe
    driver.switch_to.frame(iframe)

    # Warte auf das Eingabefeld "Start"
    from_textbox = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.ID, "From")))
    from_textbox.click()
    time.sleep(10)

    # Text eingeben
    from_textbox.send_keys("Hannover, Rosemeyerstraße 16")

    # Pfeiltaste nach unten und Enter drücken
    from_textbox.send_keys(Keys.ARROW_DOWN)
    from_textbox.send_keys(Keys.ENTER)


    to_textbox = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "To")))
    to_textbox.click()
    time.sleep(5)

    to_textbox.send_keys("Hannover, Messe/Ost (EXPO-Plaza)")
    # Pfeiltaste nach unten und Enter drücken
    from_textbox.send_keys(Keys.ARROW_DOWN)
    from_textbox.send_keys(Keys.ENTER)

    time.sleep(5)

    # HTML-Inhalt der Seite abrufen
    page_source = driver.page_source

    time.sleep(5)

    # Webdriver schließen
    driver.quit()

    # BeautifulSoup verwenden, um den HTML-Inhalt zu analysieren und zu extrahieren
    soup = BeautifulSoup(page_source, "html.parser")

     # Extract departure, arrival times, and transit information
    connections = soup.find_all(class_="lyr_tpResultOvInfo")
    print(connections)
     # Daten für die tabellarische Darstellung sammeln
    table_data = []
    for i in range(0, len(connections), 2):
        departure_info = connections[i].get_text(strip=True).replace(";", "; ").replace("DauerDauer", "Dauer").replace("pünktlich", "").replace("+", " +").replace("Umstieg1", " Umstieg: 1").replace("Umstiege2", " Umstiege: 2").replace("Minuten", " Minuten").replace("Umstieg; 1","").replace("Umstiege; 2","").replace("Abfahrt", "Abfahrt Linie")
        duration_info = connections[i+1].get_text(strip=True).replace(";", "; ").replace("DauerDauer", "Dauer").replace("pünktlich", "").replace("+", " +").replace("Umstieg1", " Umstieg: 1").replace("Umstiege2", " Umstiege: 2").replace("Minuten", " Minuten").replace("Umstieg; 1","").replace("Umstiege; 2","").replace("Abfahrt", "Abfahrt Linie")
        table_data.append([departure_info, duration_info])

    # Tabellarische Ausgabe
    headers = ["Abfahrt Schünemannplatz", "Dauer und Umstiege"]
    table_html = tabulate(table_data, headers=headers, tablefmt="html")

    return table_html
while True:
    html_table = scrape_connections()
    save_to_file(html_table, "fahrplan.txt")
    # Zeitstempel für die letzte Abfrage hinzufügen
    last_query_timestamp = time.strftime('%H:%M:%S')
    with open("last_query_timestamp.txt", 'w') as file:
        file.write(last_query_timestamp)
    time.sleep(232.443)
#print(html_table)
