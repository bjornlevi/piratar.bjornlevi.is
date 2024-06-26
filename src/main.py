# main.py

import sqlite3
import os, sys
import requests
import xmltodict
from fetch_thingmenn import fetch_thingmenn
from fetch_malaskra import fetch_malaskra
from fetch_thingskjol import fetch_thingskjol
from fetch_individual_thingskjol import fetch_individual_thingskjol
from fetch_thingmal import fetch_thingmal
from fetch_raedur import fetch_raedur
from fetch_dagskra import fetch_dagskra

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

def get_current_session(force=False):
    # Ná í upplýsingar um löggjafarþing
    print("Næ í upplýsingar um löggjafarþing")
    url = "https://www.althingi.is/altext/xml/loggjafarthing/yfirstandandi/"
    data = cache_or_fetch(url, force)

    # Extract information from the parsed data
    yfirstandandi = data['löggjafarþing']['þing']

    try:
        return yfirstandandi[u'@númer']
    except:
        print(u'Tókst ekki að ná í núverandi þing, reyndu aftur síðar. Mögulega er xml þjónusta þingsins niðri')
        sys.exit(0)

def main():
    force = False

    if len(sys.argv) > 1 and sys.argv[1] == "force":
        force = True

    # Set the base paths
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_PATH, '..', 'db', 'althingi.db')
    CACHE_PATH = os.path.join(BASE_PATH, '..', 'cache')


    # Ensure cache directory exists
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    # Remove old database
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except Exception as e:
        sys.exit(0)

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    current_session = get_current_session(force)
    fetch_thingmenn(current_session, conn, force)
    fetch_malaskra(current_session, conn, force)
    fetch_thingskjol(current_session, conn, force)
    fetch_individual_thingskjol(conn, force)
    fetch_thingmal(conn, force)
    fetch_raedur(current_session, conn, force)
    fetch_dagskra(conn, force)

    conn.close()

if __name__ == '__main__':
    main()
