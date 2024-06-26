# fetch_raedur.py

import requests
import xmltodict
import os
import sqlite3
from bs4 import BeautifulSoup

def cache_file(url, contents):
    file_name = "cache/"+url.replace('/','-')
    with open(file_name, "w") as f:
        f.write(contents)

def get_xml_data(url):
    response = requests.get(url)
    cache_file(url, response.text)
    return xmltodict.parse(response.text)

def cache_or_fetch(url, force):
    os.makedirs("cache", exist_ok=True)
    file_name = "cache/"+url.replace('/','-')
    if force:
        return get_xml_data(url)
    elif os.path.exists(file_name):
        with open(file_name, "r") as f:
            return xmltodict.parse(f.read())
    else:
        return get_xml_data(url)

def fetch_raedur(current_session, conn, force=False):
    cursor = conn.cursor()

    print("Næ i ræður")
    url = "https://www.althingi.is/altext/xml/raedulisti/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raedur (
            id INTEGER PRIMARY KEY,
            raedumadur TEXT,
            dagur TEXT,
            mal_numer INTEGER,
            mal_heiti TEXT,
            mal_tegund TEXT,
            raeda_hofst TEXT,
            raeda_lauk TEXT,
            raeda_texti TEXT,
            raeda_html TEXT
        )
    ''')
    conn.commit()

    counter = 1
    for raeda in data['ræðulisti']['ræða']:
        raedumadur = raeda['ræðumaður']['nafn']
        dagur = raeda['dagur']
        mal_numer = raeda['mál']['málsnúmer']
        mal_heiti = raeda['mál']['málsheiti']
        raeda_hofst = raeda['ræðahófst']
        raeda_lauk = raeda['ræðulauk']
        try:
            raeda_html = raeda['slóðir']['html']
        except:
            raeda_html = ""

        if 'xml' in raeda['slóðir']:
            try:
                raeda_data = cache_or_fetch(raeda['slóðir']['xml'], force)
                soup_data = xmltodict.unparse(raeda_data)
                soup = BeautifulSoup(soup_data, 'lxml-xml')
                for mgr in soup.find_all('mgr'):
                    mgr.replace_with('###'+mgr.get_text()+'###')
                raeda_texti = soup.find('ræðutexti').get_text()
                raeda_texti = raeda_texti.replace('\n', ' ')
                raeda_texti = raeda_texti.replace('  ', ' ')
                raeda_texti = raeda_texti.replace('###', '\n')
            except Exception as e:
                print(e)
                raeda_texti = "Villa í XML ræðutexta, vinsamlega smellið á tengilinn hér fyrir ofan."
            mal_tegund = raeda_data['ræða']['umsýsla']['mál']["@málstegund"]
        else:
            raeda_texti = ""
            mal_tegund = ""

        if counter % 20 == 0:
            print(str(round(counter/len(data['ræðulisti']['ræða']), 2) * 100) + "%", end='                \r')
        counter += 1

        cursor.execute('''
            INSERT INTO raedur (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html))

    conn.commit()
