# -*- coding: utf-8 -*-
import requests
import xmltodict
import sqlite3
import sys, os
import json
from bs4 import BeautifulSoup

# Set the base paths
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_PATH, '..', 'db', 'althingi.db')
CACHE_PATH = os.path.join(BASE_PATH, '..', 'cache')

# Ensure cache directory exists
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

# Force update flag
force = False
try:
    if sys.argv[1] == "True":
        force = True
except:
    pass

def cache_file(url, contents):
    file_name = os.path.join(CACHE_PATH, url.replace('/', '-'))
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(contents)

def get_xml_data(url):
    # Get new files
    response = requests.get(url)
    # Cache file
    cache_file(url, response.text)
    return xmltodict.parse(response.text)

# Functions
def cache_or_fetch(url, force):
    file_name = os.path.join(CACHE_PATH, url.replace('/', '-'))

    if force:
        return get_xml_data(url)
    else:
        if os.path.exists(file_name):
            # File exists, return file contents
            with open(file_name, "r", encoding='utf-8') as f:
                return xmltodict.parse(f.read())
        else:
            return get_xml_data(url)

def get_thingflokkur(url):
    data = cache_or_fetch(url, force)
    if isinstance(data['þingmaður']['þingsetur']['þingseta'], list):
        return data['þingmaður']['þingsetur']['þingseta'][-1]['þingflokkur']['#text']
    else:
        return data['þingmaður']['þingsetur']['þingseta']['þingflokkur']['#text']

# Remove old database
try:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
except Exception as e:
    sys.exit(0)

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thingmenn (
            id INTEGER PRIMARY KEY,
            nafn TEXT,
            faedingardagur DATE,
            skammstofun TEXT,
            thingflokkur TEXT
        )
    ''')

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
    conn.commit()

create_tables()

# Fetch data
def fetch_data():
    # Ná í upplýsingar um löggjafarþing
    print("Næ í upplýsingar um löggjafarþing")
    url = "https://www.althingi.is/altext/xml/loggjafarthing/yfirstandandi/"
    data = cache_or_fetch(url, force)

    # Extract information from the parsed data
    yfirstandandi = data['löggjafarþing']['þing']

    try:
        current_session = yfirstandandi[u'@númer']
    except:
        print(u'Tókst ekki að ná í núverandi þing, reyndu aftur síðar. Mögulega er xml þjónusta þingsins niðri')
        sys.exit(0)

    print(f"Næ í gögn um þing númer: {current_session}")

    # Ná í upplýsingar um þingmenn
    print("Næ í upplýsingar um þingmenn")
    url = "https://www.althingi.is/altext/xml/thingmenn/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    # Safna saman upplýsingum um þingmenn í lista
    data_list = []

    # Extract information from the data
    thingmenn_list = data['þingmannalisti']['þingmaður']

    counter = 0
    for thingmadur in thingmenn_list:
        counter += 1
        if counter % 20 == 0:
            print(str(round(counter / len(thingmenn_list), 2) * 100) + "%", end='                \r')
        id_value = int(thingmadur['@id'])
        nafn = thingmadur['nafn']
        faedingardagur = thingmadur['fæðingardagur']
        skammstofun = thingmadur['skammstöfun']

        # Extracting URLs from the 'xml' and 'html' elements
        thingseta = thingmadur['xml']['þingseta']
        thingflokkur = get_thingflokkur(thingseta)

        data_list.append((id_value, nafn, faedingardagur, skammstofun, thingflokkur))

    # Insert the data into the SQLite database
    cursor.executemany('''
        INSERT INTO thingmenn (id, nafn, faedingardagur, skammstofun, thingflokkur)
        VALUES (?, ?, ?, ?, ?)
    ''', data_list)

    # Commit the changes
    conn.commit()

    # Ná í málalista þings
    print("Næ í málaskrá þingsins")
    url = "https://www.althingi.is/altext/xml/thingmalalisti/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    # Extract information from the parsed data and insert into the database
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

        # Use a transaction for atomicity
        conn.execute('BEGIN')

        try:
            # Try to insert the record
            cursor.execute('''
                INSERT OR IGNORE INTO malaskra (malsnumer, thingnumer, malsflokkur, malsheiti, efnisgreining, malsstegund, html, xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (malsnumer, thingnumer, malsflokkur, malsheiti, efnisgreining, malsstegund, html, xml))

            # Commit the changes
            conn.commit()

        except sqlite3.Error as e:
            # Rollback the transaction in case of an error
            conn.rollback()

    # Ná í upplýsingar um þingskjöl
    print("Næ i þingskjalalista")
    url = "https://www.althingi.is/altext/xml/thingskjol/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    # Extract information from the parsed data and insert or update in the database
    thingskjol_list = data['þingskjöl']['þingskjal']

    for thingskjal in thingskjol_list:
        skjalsnumer = int(thingskjal['@skjalsnúmer'])
        thingnumer = int(thingskjal['@þingnúmer'])
        utbyting = thingskjal['útbýting']
        skjalategund = thingskjal['skjalategund']
        xml = thingskjal['slóð']['xml']

        # Use a transaction for atomicity
        conn.execute('BEGIN')

        try:
            # Try to insert the record
            cursor.execute('''
                INSERT OR IGNORE INTO thingskjol (skjalsnumer, thingnumer, utbyting, skjalategund, xml)
                VALUES (?, ?, ?, ?, ?)
            ''', (skjalsnumer, thingnumer, utbyting, skjalategund, xml))

            # Commit the changes
            conn.commit()

        except sqlite3.Error as e:
            # Rollback the transaction in case of an error
            conn.rollback()

    # Ná í upplýsingar um einstaka þingskjöl
    print("Næ í upplýsingar um einstaka þingskjöl")
    cursor.execute('select xml from thingskjol')
    xml_link_list = cursor.fetchall()  # listi af xml tenglum fyrir öll þingskjöl

    counter = 0
    for xml_link in xml_link_list:
        counter += 1
        try:
            data = cache_or_fetch(xml_link[0].replace('&amp;', '&'), force)
        except:
            print(xml_link)
            continue
        if counter % 20 == 0:
            print(str(round(counter / len(xml_link_list), 2) * 100) + "%", end='               \r')

        # Extract information from the parsed data and insert or update in the database
        thingskjal = data['þingskjal']['þingskjal']
        skjalsnumer = int(thingskjal['@skjalsnúmer'])
        mal = data['þingskjal']['málalisti']['mál']
        malsnumer = int(mal['@málsnúmer'])
        thingnumer = int(thingskjal['@þingnúmer'])
        utbyting = thingskjal['útbýting']
        skjalategund = thingskjal['skjalategund']

        # Insert or ignore into thingskjal table
        cursor.execute('''
            INSERT OR IGNORE INTO thingskjal (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund)
            VALUES (?, ?, ?, ?, ?)
        ''', (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund))

        # Insert or ignore into flutningsmaður table
        try:
            flutningsmenn = ''
            try:
                flutningsmenn = thingskjal['flutningsmenn']['flutningsmaður']  # can be either list or dict
            except:
                flutningsmenn = thingskjal['flutningsmenn']['nefnd']['flutningsmaður']  # is a list

            if isinstance(flutningsmenn, list):
                for flutningsmadur in flutningsmenn:
                    rada = int(flutningsmadur['@röð'])
                    nafn = flutningsmadur['nafn']
                    xml = flutningsmadur['xml']
                    cursor.execute('''
                        INSERT OR IGNORE INTO flutningsmadur (skjalsnumer, rada, nafn, xml)
                        VALUES (?, ?, ?, ?)
                    ''', (skjalsnumer, rada, nafn, xml))
            elif isinstance(flutningsmenn, dict):
                rada = int(flutningsmenn['@röð'])
                nafn = ''
                try:
                    radherra = flutningsmenn['ráðherra']
                except:
                    radherra = ''
                nafn = flutningsmenn['nafn']
                xml = flutningsmenn['xml']
                cursor.execute('''
                    INSERT OR IGNORE INTO flutningsmadur (skjalsnumer, rada, nafn, radherra, xml)
                    VALUES (?, ?, ?, ?, ?)
                ''', (skjalsnumer, rada, nafn, radherra, xml))
        except:
            # þetta geta verið þingskjöl á við nefndarálit, lög í heild, etc. Sleppa
            pass
        # Commit the changes
        conn.commit()

    # Ná í upplýsingar um einstaka mál
    print("Næ í upplýsingar um einstaka mál")

    # Create table if not exists
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

    cursor.execute('select xml from malaskra')
    xml_link_list = cursor.fetchall()

    counter = 0
    for xml_link in xml_link_list:
        # Ná í upplýsingar um öll mál
        counter += 1
        data = cache_or_fetch(xml_link[0], force)
        if counter % 20 == 0:
            print(str(round(counter / len(xml_link_list), 2) * 100) + "%", end='                \r')

        # Extract relevant information from the parsed data and insert into the database
        mal = data['þingmál']['mál']
        malnumer = mal['@málsnúmer']
        thingnumer = mal['@þingnúmer']
        malsheiti = mal['málsheiti']
        malstegund = mal['málstegund']['heiti']
        stadamals = ''
        try:
            stadamals = mal['staðamáls']
        except:
            pass  # beiðni um skýrslu sem er fær ekki stöðu
        framsogumadur = ''
        try:
            framsogumadur = mal['framsogumenn']['framsogumadur']['nafn']
        except:
            pass
        html = mal['slóð']['html']
        xml = mal['slóð']['xml']
        # Find the first atkvæðagreiðsla containing the 'til' tag
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

        # Insert or ignore the data into the database
        cursor.execute('''
            INSERT OR IGNORE INTO thingmal
            (malnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (malnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml))

        # Commit the changes
        conn.commit()

    # Næ í ræður
    print("Næ i ræður")
    url = "https://www.althingi.is/altext/xml/raedulisti/?lthing=" + current_session
    data = cache_or_fetch(url, force)

    # Create table if not exists
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

    # Iterate through the XML data and insert into the database
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
            raeda_html = ""  # ræður forseta eru ekki með html slóð

        if 'xml' in raeda['slóðir']:
            try:
                raeda_data = cache_or_fetch(raeda['slóðir']['xml'], force)
                soup_data = xmltodict.unparse(raeda_data)
                soup = BeautifulSoup(soup_data, 'lxml-xml')
                for mgr in soup.find_all('mgr'):
                    mgr.replace_with('###' + mgr.get_text() + '###')  # placeholder fyrir málsgrein
                raeda_texti = soup.find('ræðutexti').get_text()
                raeda_texti = raeda_texti.replace('\n', ' ')  # hreinsa öll newline
                raeda_texti = raeda_texti.replace('  ', ' ')  # hreinsa öll tvöföld línubil
                raeda_texti = raeda_texti.replace('###', '\n')  # setja inn málsgreinar aftur
            except Exception as e:
                print(e)
                raeda_texti = "Villa í XML ræðutexta, vinsamlega smellið á tengilinn hér fyrir ofan."
            mal_tegund = raeda_data['ræða']['umsýsla']['mál']["@málstegund"]
        else:
            raeda_texti = ""
            mal_tegund = ""

        if counter % 20 == 0:
            print(str(round(counter / len(data['ræðulisti']['ræða']), 2) * 100) + "%", end='                \r')
        counter += 1

        # Insert into the database
        cursor.execute('''
            INSERT INTO raedur (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html))

    conn.commit()

    # Ná í dagskrá þingsins
    print("Næ i dagskrá þingsins")
    url = "https://www.althingi.is/altext/xml/dagskra/thingfundur/"
    data = cache_or_fetch(url, force)

    try:
        # Insert parsed data into the SQLite tables
        if type(data['dagskráþingfundar']['þingfundur']) is list:
            for thingfundur in data['dagskráþingfundar']['þingfundur']:
                thingfundur_numer = thingfundur['@númer']
                fundarheiti = thingfundur['fundarheiti']
                hefst = thingfundur['hefst']['texti']

                # Insert data from dagskrárliður elements
                for dagskrarlidur in thingfundur['dagskrá']['dagskrárliður']:
                    lidur_numer = dagskrarlidur['@númer']
                    malsnumer = dagskrarlidur['mál']['@málsnúmer']
                    malsheiti = dagskrarlidur['mál']['málsheiti']
                    malsflokkur = dagskrarlidur['mál']['@málsflokkur']
                    if 'athugasemd' in dagskrarlidur:
                        if 'skýring' in dagskrarlidur['athugasemd']:
                            skyring = dagskrarlidur['athugasemd']['skýring']
                        else:
                            skyring = ''
                    else:
                        skyring = ''
                    if 'umræða' in dagskrarlidur:
                        if '#text' in dagskrarlidur['umræða']:
                            umraeda = dagskrarlidur['umræða']['#text']
                        else:
                            umraeda = ''
                    else:
                        umraeda = ''
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

            # Insert data from dagskrárliður elements
            for dagskrarlidur in thingfundur['dagskrá']['dagskrárliður']:
                lidur_numer = dagskrarlidur['@númer']
                malsnumer = dagskrarlidur['mál']['@málsnúmer']
                malsheiti = dagskrarlidur['mál']['málsheiti']
                malsflokkur = dagskrarlidur['mál']['@málsflokkur']
                if 'athugasemd' in dagskrarlidur:
                    if 'skýring' in dagskrarlidur['athugasemd']:
                        skyring = dagskrarlidur['athugasemd']['skýring']
                    else:
                        skyring = ''
                else:
                    skyring = ''
                if 'umræða' in dagskrarlidur:
                    if '#text' in dagskrarlidur['umræða']:
                        umraeda = dagskrarlidur['umræða']['#text']
                    else:
                        umraeda = ''
                else:
                    umraeda = ''
                html_link = dagskrarlidur['mál']['html']

                cursor.execute('''
                    INSERT INTO dagskra
                    (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link))

        # Commit changes and close connection
        conn.commit()
    except:
        print("Villa eða ekki komin dagskrá fyrir þingfund")

fetch_data()
conn.close()
