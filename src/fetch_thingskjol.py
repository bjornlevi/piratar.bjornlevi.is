# fetch_thingskjol.py

import requests
import xmltodict
import os
import sqlite3

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

def fetch_thingskjol(current_session, conn, force=False):
    cursor = conn.cursor()
    print("Næ i þingskjalalista")
    url = "https://www.althingi.is/altext/xml/thingskjol/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thingskjol (
            id INTEGER PRIMARY KEY,
            skjalsnumer INTEGER,
            thingnumer INTEGER,
            utbyting TEXT,
            skjalategund TEXT,
            xml TEXT,
            UNIQUE(skjalsnumer, thingnumer)
        )
    ''')

    thingskjol_list = data['þingskjöl']['þingskjal']

    for thingskjal in thingskjol_list:
        skjalsnumer = int(thingskjal['@skjalsnúmer'])
        thingnumer = int(thingskjal['@þingnúmer'])
        utbyting = thingskjal['útbýting']
        skjalategund = thingskjal['skjalategund']
        xml = thingskjal['slóð']['xml']

        conn.execute('BEGIN')

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO thingskjol (skjalsnumer, thingnumer, utbyting, skjalategund, xml)
                VALUES (?, ?, ?, ?, ?)
            ''', (skjalsnumer, thingnumer, utbyting, skjalategund, xml))

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()

