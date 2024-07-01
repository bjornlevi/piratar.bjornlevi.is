import sqlite3
from utils import cache_or_fetch

def get_thingflokkur(url, force):
    data = cache_or_fetch(url, force)
    if isinstance(data['þingmaður']['þingsetur']['þingseta'], list):
        latest_thingseta = data['þingmaður']['þingsetur']['þingseta'][-1]
    else:
        latest_thingseta = data['þingmaður']['þingsetur']['þingseta']

    thingflokkur = latest_thingseta.get('þingflokkur', {}).get('#text', '')
    return thingflokkur

def fetch_thingmenn(current_session, force):
    url = f"https://www.althingi.is/altext/xml/thingmenn/?lthing={current_session}"
    data = cache_or_fetch(url, force)
    thingmenn_list = data['þingmannalisti']['þingmaður']

    data_list = []
    counter = 0
    print("Fjöldi þingmanna: ", len(thingmenn_list))
    for thingmadur in thingmenn_list:
        counter += 1
        if counter%20 == 0:
            print(str(round(counter/len(thingmenn_list),2)*100)+"%", end='                \r')         
        id_value = int(thingmadur['@id'])
        nafn = thingmadur['nafn']
        faedingardagur = thingmadur['fæðingardagur']
        skammstofun = thingmadur.get('skammstöfun', '')  # Use .get() to avoid KeyError
        thingseta = thingmadur['xml']['þingseta']
        thingflokkur = get_thingflokkur(thingseta, force)

        data_list.append((id_value, nafn, faedingardagur, skammstofun, thingflokkur))

    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()
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
    conn.close()

if __name__ == '__main__':
    import sys
    force = False
    try:
        force = sys.argv[1].lower() == 'true'
    except IndexError:
        pass
    current_session = sys.argv[2] if len(sys.argv) > 2 else 'default_session'
    fetch_thingmenn(current_session, force)
