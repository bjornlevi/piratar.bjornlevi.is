import sqlite3
from utils import cache_or_fetch
import xmltodict
from bs4 import BeautifulSoup

def fetch_raedur(current_session, force):
    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()

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

    # Fetch speeches data
    print("Næ i ræður")
    url = f"https://www.althingi.is/altext/xml/raedulisti/?lthing={current_session}"
    data = cache_or_fetch(url, force)

    # Iterate through the XML data and insert into the database
    counter = 1
    for raeda in data['ræðulisti']['ræða']:
        raedumadur = raeda['ræðumaður']['nafn']
        dagur = raeda['dagur']
        mal_numer = raeda['mál']['málsnúmer']
        mal_heiti = raeda['mál']['málsheiti']
        raeda_hofst = raeda['ræðahófst']
        raeda_lauk = raeda['ræðulauk']
        
        raeda_html = raeda['slóðir'].get('html', "")  # Default to empty string if not present

        if 'xml' in raeda['slóðir']:
            try:
                raeda_data = cache_or_fetch(raeda['slóðir']['xml'], force)
                soup_data = xmltodict.unparse(raeda_data)
                soup = BeautifulSoup(soup_data, 'lxml-xml')
                for mgr in soup.find_all('mgr'):
                    mgr.replace_with('###'+mgr.get_text()+'###')  # Placeholder for paragraph
                raeda_texti = soup.find('ræðutexti').get_text()
                raeda_texti = raeda_texti.replace('\n', ' ')  # Remove all newlines
                raeda_texti = raeda_texti.replace('  ', ' ')  # Remove all double spaces
                raeda_texti = raeda_texti.replace('###', '\n')  # Restore paragraphs
                mal_tegund = raeda_data['ræða']['umsýsla']['mál']["@málstegund"]
            except Exception as e:
                print(e)
                raeda_texti = "Villa í XML ræðutexta, vinsamlega smellið á tengilinn hér fyrir ofan."
                mal_tegund = ""
        else:
            raeda_texti = ""
            mal_tegund = ""

        if counter % 20 == 0:
            print(f"{round(counter/len(data['ræðulisti']['ræða'])*100, 2)}%", end='                \r')
        counter += 1

        # Insert into the database
        cursor.execute('''
            INSERT INTO raedur (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (raedumadur, dagur, mal_numer, mal_heiti, mal_tegund, raeda_hofst, raeda_lauk, raeda_texti, raeda_html))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    import sys
    force = False
    try:
        force = sys.argv[1].lower() == 'true'
    except IndexError:
        pass
    current_session = sys.argv[2] if len(sys.argv) > 2 else 'default_session'
    fetch_raedur(current_session, force)
