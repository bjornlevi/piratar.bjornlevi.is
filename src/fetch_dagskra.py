# fetch_dagskra.py

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

def fetch_dagskra(conn, force=False):
    cursor = conn.cursor()

    print("Næ i dagskrá þingsins")
    url = "https://www.althingi.is/altext/xml/dagskra/thingfundur/"
    data = cache_or_fetch(url, force)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dagskra (
            thingfundur_numer INTEGER,
            fundarheiti TEXT,
            hefst TEXT,
            lidur_numer INTEGER,
            malsheiti TEXT,
            malsnumer INTEGER,
            malsstegund TEXT,
            malsflokkur TEXT,
            skyring TEXT,
            umraeda TEXT,
            html_link TEXT,
            PRIMARY KEY (thingfundur_numer, lidur_numer)
        )
    ''')

    try:
        if type(data['dagskráþingfundar']['þingfundur']) is list:
            for thingfundur in data['dagskráþingfundar']['þingfundur']:
                thingfundur_numer = thingfundur['@númer']
                fundarheiti = thingfundur['fundarheiti']
                hefst = thingfundur['hefst']['texti']

                for dagskrarlidur in thingfundur['dagskrá']['dagskrárliður']:
                    lidur_numer = dagskrarlidur['@númer']
                    malsnumer = dagskrarlidur['mál']['@málsnúmer']
                    malsheiti = dagskrarlidur['mál']['málsheiti']
                    malsflokkur = dagskrarlidur['mál']['@málsflokkur']
                    skyring = dagskrarlidur.get('athugasemd', {}).get('skýring', '')
                    umraeda = dagskrarlidur.get('umræða', {}).get('#text', '')
                    html_link = dagskrarlidur['mál']['html']

                    cursor.execute('''
                        INSERT INTO dagskra
                        (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link))
        else:
            thingfundur = data['dagskráþingfundar']['þingfundur']
            thingfundur_numer = thingfundur['@númer']
            fundarheiti = thingfundur['fundarheiti']
            hefst = thingfundur['hefst']['texti']

            for dagskrarlidur in thingfundur['dagskrá']['dagskrárliður']:
                lidur_numer = dagskrarlidur['@númer']
                malsnumer = dagskrarlidur['mál']['@málsnúmer']
                malsheiti = dagskrarlidur['mál']['málsheiti']
                malsflokkur = dagskrarlidur['mál']['@málsflokkur']
                skyring = dagskrarlidur.get('athugasemd', {}).get('skýring', '')
                umraeda = dagskrarlidur.get('umræða', {}).get('#text', '')
                html_link = dagskrarlidur['mál']['html']

                cursor.execute('''
                    INSERT INTO dagskra
                    (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link))

        conn.commit()
    except:
        print("Villa eða ekki komin dagskrá fyrir þingfund")

