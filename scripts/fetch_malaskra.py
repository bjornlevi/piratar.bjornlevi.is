import sqlite3
from utils import cache_or_fetch

def fetch_malaskra(current_session, force):
    url = f"https://www.althingi.is/altext/xml/thingmalalisti/?lthing={current_session}"
    data = cache_or_fetch(url, force)
    mal_list = data['málaskrá']['mál']

    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS malaskra (
            malsnumer INTEGER PRIMARY KEY,
            thingnumer INTEGER,
            malsheiti TEXT,
            malstegund TEXT,
            stadamals TEXT,
            framsogumadur TEXT,
            nefnd TEXT,
            html TEXT,
            xml TEXT,
            UNIQUE(malsnumer, thingnumer)
        )
    ''')

    counter = 0
    print("Fjöldi mála: ", len(mal_list))
    for m in mal_list:
        data = cache_or_fetch(m['xml'], force)
        if 'þingmál' in data:
            mal = data['þingmál']['mál']
            counter += 1
            if counter % 20 == 0:
                print(f"{round(counter/len(mal_list)*100, 2)}%", end='                \r')
            malsnumer = int(mal['@málsnúmer'])
            thingnumer = int(mal['@þingnúmer'])
            malsheiti = mal['málsheiti']
            malstegund = mal['málstegund']['heiti']
            stadamals = ''
            try:
                stadamals = mal['staðamáls']
            except:
                pass #beiðni um skýrslu sem er fær ekki stöðu
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
                INSERT OR IGNORE INTO malaskra
                (malsnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (malsnumer, thingnumer, malsheiti, malstegund, stadamals, framsogumadur, nefnd, html, xml))
            # Commit the changes
            conn.commit()
        else:
            continue

    conn.close()

if __name__ == '__main__':
    import sys
    force = False
    try:
        force = sys.argv[1].lower() == 'true'
    except IndexError:
        pass
    current_session = sys.argv[2] if len(sys.argv) > 2 else 'default_session'
    fetch_malaskra(current_session, force)
