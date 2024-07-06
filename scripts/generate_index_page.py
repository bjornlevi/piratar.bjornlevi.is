import sqlite3
from jinja2 import Environment, FileSystemLoader
import os

def fetch_mal_with_thingskjal_entries(db_path):
    print(f"Connecting to database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT 
            m.malsnumer, 
            t.skjalsnumer, 
            m.malsheiti, 
            t.skjalategund,
            m.stadamals AS "staða máls", 
            CASE 
                WHEN f.radherra IS NOT NULL AND f.radherra != '' THEN f.radherra 
                ELSE f.nafn 
            END AS flutningsmadur, 
            m.nefnd, 
            m.html AS "html for mal", 
            t.utbyting, 
            t.html AS "html for thingskjal",
            tm.thingflokkur,
            ROW_NUMBER() OVER (PARTITION BY m.malsnumer ORDER BY t.skjalsnumer) as row_num
        FROM 
            malaskra m
        LEFT JOIN 
            (SELECT DISTINCT skjalsnumer, malsnumer, skjalategund, utbyting, html FROM thingskjal) t 
            ON m.malsnumer = t.malsnumer
        LEFT JOIN 
            (SELECT DISTINCT skjalsnumer, nafn, rod, radherra FROM flutningsmadur WHERE rod = 1) f 
            ON t.skjalsnumer = f.skjalsnumer
        LEFT JOIN 
            (SELECT DISTINCT nafn, thingflokkur FROM thingmenn) tm 
            ON f.nafn = tm.nafn
        ORDER BY 
            m.malsnumer, t.skjalsnumer;
    ''')
    entries = cursor.fetchall()
    conn.close()
    print(f"Fetched {len(entries)} entries from the database")
    return [dict(malsnumer=row[0], skjalsnumer=row[1], malsheiti=row[2], skjalategund=row[3], stadamals=row[4], flutningsmadur=row[5], nefnd=row[6], html_mal=row[7], utbyting=row[8], html_thingskjal=row[9], thingflokkur=row[10], row_num=row[11]) for row in entries]

def generate_html(entries):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index_template.html')
    output = template.render(entries=entries)
    os.makedirs('output', exist_ok=True)
    with open('output/index.html', 'w') as f:
        f.write(output)
    print("HTML file generated successfully")

def main():
    db_path = os.path.abspath('thing.db')
    print(f"Absolute database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    entries = fetch_mal_with_thingskjal_entries(db_path)
    generate_html(entries)

if __name__ == '__main__':
    main()
