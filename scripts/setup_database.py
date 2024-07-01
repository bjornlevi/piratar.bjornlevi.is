import sqlite3

def setup_database():
    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flutningsmadur (
            malsnumer INTEGER,
            thingnumer INTEGER,
            rod INTEGER,
            nafn TEXT,
            radherra TEXT,
            skjalsnumer INTEGER
        )
    ''')

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
    conn.close()

if __name__ == '__main__':
    setup_database()
