# fetch_thingmenn.py

import requests
import xmltodict
import os
import sys

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

def get_thingflokkur(url, force):
    data = cache_or_fetch(url, force)
    if isinstance(data['þingmaður']['þingsetur']['þingseta'], list):
        return data['þingmaður']['þingsetur']['þingseta'][-1]['þingflokkur']['#text']
    else:
        return data['þingmaður']['þingsetur']['þingseta']['þingflokkur']['#text']

def fetch_thingmenn(current_session, conn, force=False):
    cursor = conn.cursor()

    print("Næ í upplýsingar um þingmenn")
    url = "https://www.althingi.is/altext/xml/thingmenn/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    data_list = []
    thingmenn_list = data['þingmannalisti']['þingmaður']

    counter = 0
    for thingmadur in thingmenn_list:
        counter += 1
        if counter % 20 == 0:
            print(str(round(counter/len(thingmenn_list), 2) * 100) + "%", end='                \r')
        id_value = int(thingmadur['@id'])
        nafn = thingmadur['nafn']
        faedingardagur = thingmadur['fæðingardagur']
        skammstofun = thingmadur['skammstöfun']

        thingseta = thingmadur['xml']['þingseta']
        thingflokkur = get_thingflokkur(thingseta, force)

        data_list.append((id_value, nafn, faedingardagur, skammstofun, thingflokkur))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thingmenn (
            id INTEGER PRIMARY KEY,
            nafn TEXT,
            faedingardagur DATE,
            skammstofun TEXT,
            thingflokkur TEXT
        )
    ''')

    cursor.executemany('''
        INSERT INTO thingmenn (id, nafn, faedingardagur, skammstofun, thingflokkur)
        VALUES (?, ?, ?, ?, ?)
    ''', data_list)

    conn.commit()
