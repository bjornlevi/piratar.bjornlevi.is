import sqlite3
from utils import cache_or_fetch

def fetch_dagskra(current_session, force):
    url = f"https://www.althingi.is/altext/xml/dagskra/thingfundur/"
    data = cache_or_fetch(url, force)

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

    try:
        if isinstance(data['dagskráþingfundar']['þingfundur'], list):
            pass
    except:
        print("Enginn þingfundur")
        return

    if isinstance(data['dagskráþingfundar']['þingfundur'], list):
        for thingfundur in data['dagskráþingfundar']['þingfundur']:
            thingfundur_numer = thingfundur['@númer']
            fundarheiti = thingfundur['fundarheiti']
            hefst = thingfundur['hefst']['texti']

            for dagskrarlidur in thingfundur['dagskrá']['dagskrárliður']:
                lidur_numer = dagskrarlidur['@númer']
                malsnumer = dagskrarlidur['mál']['@málsnúmer']
                malsheiti = dagskrarlidur['mál']['málsheiti']
                malsflokkur = dagskrarlidur['mál']['@málsflokkur']
                skyring = dagskrarlidur['athugasemd'].get('skýring', '') if 'athugasemd' in dagskrarlidur else ''
                umraeda = dagskrarlidur['umræða'].get('#text', '') if 'umræða' in dagskrarlidur else ''
                html_link = dagskrarlidur['mál']['html']

                cursor.execute('''
                   INSERT INTO dagskra
                   (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link))
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
            skyring = dagskrarlidur['athugasemd'].get('skýring', '') if 'athugasemd' in dagskrarlidur else ''
            umraeda = dagskrarlidur['umræða'].get('#text', '') if 'umræða' in dagskrarlidur else ''
            html_link = dagskrarlidur['mál']['html']

            cursor.execute('''
                INSERT INTO dagskra
                (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (thingfundur_numer, fundarheiti, hefst, lidur_numer, malsnumer, malsheiti, malsflokkur, skyring, umraeda, html_link))

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
    fetch_dagskra(current_session, force)

