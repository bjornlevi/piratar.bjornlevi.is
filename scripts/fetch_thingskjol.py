import sqlite3
from utils import cache_or_fetch

def fetch_thingskjol(current_session, force):
    url = f"https://www.althingi.is/altext/xml/thingskjol/?lthing={current_session}"
    data = cache_or_fetch(url, force)
    
    try:
        thingskjol_list = data['þingskjöl']['þingskjal']
    except:
        print("Failed to get data", data)
        return

    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flutningsmadur (
            malsnumer INTEGER,
            skjalsnumer INTEGER,
            thingnumer INTEGER,
            rod INTEGER,
            nafn TEXT,
            radherra TEXT
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
            UNIQUE(skjalsnumer, thingnumer)
        )
    ''')
    conn.commit()

    counter = 0
    print("Fjöldi þingskjala: ", len(thingskjol_list))
    for ts in thingskjol_list:
        data = cache_or_fetch(ts['slóð']['xml'], force)
        counter += 1
        if counter % 20 == 0:
            print(f"{round(counter/len(thingskjol_list)*100, 2)}%", end='                \r')
        # Extract information from the parsed data and insert or update in the database
        thingskjal = data['þingskjal']['þingskjal']
        skjalsnumer = int(thingskjal['@skjalsnúmer'])
        mal = data['þingskjal']['málalisti']['mál']
        malsnumer = int(mal['@málsnúmer'])    
        thingnumer = int(thingskjal['@þingnúmer'])
        utbyting = thingskjal['útbýting']
        skjalategund = thingskjal['skjalategund']
        html = ''
        try:
            html = thingskjal['slóð']['html']
        except:
            pass

        # Insert or ignore into thingskjal table
        cursor.execute('''
            INSERT OR IGNORE INTO thingskjal (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund, html)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (skjalsnumer, malsnumer, thingnumer, utbyting, skjalategund, html))

        # Insert or ignore into flutningsmaður table
        try:
            flutningsmenn = ''
            try: 
                flutningsmenn = thingskjal['flutningsmenn']['flutningsmaður'] #can be either list or dict
            except:
                flutningsmenn = thingskjal['flutningsmenn']['nefnd']['flutningsmaður'] #is a list
            #dæmi: 
            '''
            [
                {'@röð': '1', '@id': '1449', 'nafn': 'Friðjón R. Friðjónsson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1449'}, 
                {'@röð': '2', '@id': '1176', 'nafn': 'Vilhjálmur Árnason', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1176'}, 
                {'@röð': '3', '@id': '688', 'nafn': 'Jón Gunnarsson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=688'}, 
                {'@röð': '4', '@id': '1039', 'nafn': 'Bryndís Haraldsdóttir', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1039'}
            ]
            '''
            # þarf að laga fyrir flutning nefndar
            #dæmi:
            '''
            {
            '@skjalsnúmer': '635', '@þingnúmer': '154', '@málsflokkur': 'A', 'útbýting': '2023-11-28 15:01', 'skjalategund': 'frumvarp nefndar', 
            'flutningsmenn': 
                {'nefnd': 
                    {
                    '@id': '203', 'hluti': None, 'heiti': 'atvinnuveganefnd', 
                    'flutningsmaður': 
                        [
                            {'@röð': '1', '@id': '1345', 'nafn': 'Þórarinn Ingi Pétursson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1345'}, 
                            {'@röð': '2', '@id': '1370', 'nafn': 'Lilja Rannveig Sigurgeirsdóttir', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1370'}, 
                            {'@röð': '3', '@id': '1425', 'nafn': 'Gísli Rafn Ólafsson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1425'}, 
                            {'@röð': '4', '@id': '1157', 'nafn': 'Ásmundur Friðriksson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1157'}, 
                            {'@röð': '5', '@id': '1012', 'nafn': 'Bjarkey Olsen Gunnarsdóttir', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1012'}, 
                            {'@röð': '6', '@id': '1276', 'nafn': 'Hanna Katrín Friðriksson', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1276'}, 
                            {'@röð': '7', '@id': '999', 'nafn': 'Óli Björn Kárason', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=999'}, 
                            {'@röð': '8', '@id': '1332', 'nafn': 'Inga Sæland', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1332'}
                        ]
                    }
                }, 
            'slóð': {'html': 'http://www.althingi.is/altext/154/s/0635.html', 'pdf': 'http://www.althingi.is/altext/pdf/154/s/0635.pdf'}}
            '''
            # þarf að taka tillit til þess ef ráðherra er flutningsmaður
            #dæmi: 
            #{'@röð': '1', '@id': '730', 'ráðherra': 'matvælaráðherra', 'nafn': 'Svandís Svavarsdóttir', 'xml': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=730'}

            if isinstance(flutningsmenn, list):
                for flutningsmadur in flutningsmenn:
                    rod = int(flutningsmadur['@röð'])
                    nafn = flutningsmadur['nafn']
                    cursor.execute('''
                        INSERT INTO flutningsmadur (malsnumer, skjalsnumer, rod, nafn, thingnumer)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (malsnumer, skjalsnumer, rod, nafn, thingnumer))
                    conn.commit()
            elif isinstance(flutningsmenn, dict):
                rod = int(flutningsmenn['@röð'])
                nafn = ''
                try:
                    radherra = flutningsmenn['ráðherra']
                except:
                    radherra = ''
                nafn = flutningsmenn['nafn']
                cursor.execute('''
                    INSERT INTO flutningsmadur (malsnumer, skjalsnumer, rod, nafn, radherra, thingnumer)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (malsnumer, skjalsnumer, rod, nafn, radherra, thingnumer))
                conn.commit()
        except Exception as e:
            #þetta geta verið þingskjöl á við nefndarálit, lög í heild, etc. Sleppa
            pass
        # Commit the changes
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
    fetch_thingskjol(current_session, force)
