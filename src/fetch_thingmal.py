# fetch_thingmal.py

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

def fetch_thingmal(conn, force=False):
    cursor = conn.cursor()

    cursor.execute('select xml from malaskra')
    xml_link_list = cursor.fetchall()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thingmal (
            malnumer INTEGER PRIMARY KEY,
            thingnumer INTEGER,
            malsheiti TEXT,
            malstegund TEXT,
            stadamals TEXT,
            framsogumadur TEXT,
            nefnd TEXT,
            html TEXT,
            xml TEXT,
            UNIQUE(malnumer, thingnumer)
        )
    ''')

    counter = 0
    for xml_link in xml_link_list:
        counter += 1
        data = cache_or_fetch(xml_link[0], force)
        if counter % 20 == 0:
            print(str(round(counter/len(xml_link_list), 2) * 100) + "%", end='                \r')

        mal = data['þingmál']['mál']
        malnumer = mal['@málsnúmer']
        thingnumer = mal['@þingnúmer']
        malsheiti = mal['málsheiti']
        malstegund = mal['málstegund']['heiti']
        stadamals = mal.get('staðamáls', '')
        framsogumadur = mal.get('framsogumenn', {}).get('framsogumadur', {}).get('nafn', '')
        html = mal['slóð']['html']
        xml = mal['slóð']['xml']
        nefnd = ''
        if 'atkvæðagreiðslur' in data['þingmál']:
            try:
                at = data['þingmál']['atkvæðagreiðslur']['atkvæðagreiðsla']
                for a in at:
                    if 'til' in a:
                        nefnd = a['til']['#text']
                        break
            except:
                pass

        cursor.execute('''
            INSERT OR IGNORE INTO thingmal
            (malnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (malnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml))

        conn.commit()
