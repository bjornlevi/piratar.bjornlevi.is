# fetch_malaskra.py

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

def fetch_malaskra(current_session, conn, force=False):
    cursor = conn.cursor()
    print("Næ í málaskrá þingsins")
    url = "https://www.althingi.is/altext/xml/thingmalalisti/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS malaskra (
            id INTEGER PRIMARY KEY,
            malsnumer INTEGER,
            thingnumer INTEGER,
            malsflokkur TEXT,
            malsheiti TEXT,
            efnisgreining TEXT,
            malsstegund TEXT,
            html TEXT,
            xml TEXT,
            UNIQUE(malsnumer, thingnumer)
        )
    ''')

    mal_list = data['málaskrá']['mál']

    for mal in mal_list:
        malsnumer = int(mal['@málsnúmer'])
        thingnumer = int(mal['@þingnúmer'])
        malsflokkur = mal['@málsflokkur']
        malsheiti = mal['málsheiti']
        efnisgreining = mal['efnisgreining'] if 'efnisgreining' in mal else None
        malsstegund = mal['málstegund']['heiti']
        html = mal['html']
        xml = mal['xml']

        conn.execute('BEGIN')

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO malaskra (malsnumer, thingnumer, malsflokkur, malsheiti, efnisgreining, malsstegund, html, xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (malsnumer, thingnumer, malsflokkur, malsheiti, efnisgreining, malsstegund, html, xml))

            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()

