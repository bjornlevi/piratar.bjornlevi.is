# fetch_individual_thingskjol.py

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

def fetch_individual_thingskjol(conn, force=False):
    cursor = conn.cursor()

    cursor.execute('select xml from thingskjol')
    xml_link_list = cursor.fetchall()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thingskjal (
            id INTEGER PRIMARY KEY,
            skjalsnumer INTEGER,
            thingnumer INTEGER,
            malsnumer INTEGER,
            utbyting TEXT,
            skjalategund TEXT,      
            html TEXT,
            pdf TEXT,
            UNIQUE(skjalsnumer, thingnumer)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flutningsmadur (
            id INTEGER PRIMARY KEY,
            skjalsnumer INTEGER,
            rada INTEGER,
            nafn TEXT,
            radherra TEXT,
            xml TEXT
        )
    ''')
    conn.commit()

    counter = 0
    for xml_link in xml_link_list:    
        counter += 1
        try:
            data = cache_or_fetch(xml_link[0], force)
        except:
            print(xml_link)
            continue
        if counter % 20 == 0:
            print(str(round(counter/len(xml_link_list), 2) * 100) + "%", end='               \r')

        thingskjal = data['þingskjal']['þingskjal']
        skjalsnumer = int(thingskjal['@skjalsnúmer'])
        mal = data['þingskjal']['málalisti']['mál']
        malsnumer = int(mal['@málsnúmer'])    
        thingnumer = int(thingskjal['@þingnúmer'])
        utbyting = thingskjal['útbýting']
        skjalategund = thingskjal['skjalategund']

        cursor.execute('''
            INSERT OR IGNORE INTO thingskjal (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund)
            VALUES (?, ?, ?, ?, ?)
        ''', (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund))

        try:
            flutningsmenn = thingskjal['flutningsmenn']['flutningsmaður']
            if isinstance(flutningsmenn, list):
                for flutningsmadur in flutningsmenn:
                    rada = int(flutningsmadur['@röð'])
                    nafn = flutningsmadur['nafn']
                    xml = flutningsmadur['xml']
                    cursor.execute('''
                        INSERT OR IGNORE INTO flutningsmadur (skjalsnumer, rada, nafn, xml)
                        VALUES (?, ?, ?, ?)
                    ''', (skjalsnumer, rada, nafn, xml))
            else:
                rada = int(flutningsmenn['@röð'])
                nafn = flutningsmenn['nafn']
                radherra = flutningsmenn.get('ráðherra', '')
                xml = flutningsmenn['xml']
                cursor.execute('''
                    INSERT OR IGNORE INTO flutningsmadur (skjalsnumer, rada, nafn, radherra, xml)
                    VALUES (?, ?, ?, ?, ?)
                ''', (skjalsnumer, rada, nafn, radherra, xml))
        except:
            pass

        conn.commit()
