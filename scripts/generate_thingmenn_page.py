import sqlite3
import os
from jinja2 import Environment, FileSystemLoader

def fetch_thingmenn_entries(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch thingmenn entries, sorted alphabetically by nafn with Icelandic collation
    cursor.execute('''
        SELECT id, nafn, faedingardagur, skammstofun, thingflokkur 
        FROM thingmenn
        ORDER BY nafn COLLATE NOCASE
    ''')
    thingmenn = cursor.fetchall()

    entries = []
    for thingmadur in thingmenn:
        id, nafn, faedingardagur, skammstofun, thingflokkur = thingmadur
        
        # Fetch thingskjol entries where thingmadur is the first flutningsmadur (rod = 1) and include malsheiti
        cursor.execute('''
            SELECT DISTINCT t.skjalsnumer, t.malsnumer, t.skjalategund, t.utbyting, t.html, m.malsheiti
            FROM thingskjal t
            JOIN flutningsmadur f ON t.skjalsnumer = f.skjalsnumer
            JOIN malaskra m ON t.malsnumer = m.malsnumer
            WHERE f.nafn = ? AND f.rod = 1
            ORDER BY CAST(t.skjalsnumer AS INTEGER)
        ''', (nafn,))
        thingskjol = cursor.fetchall()

        entries.append({
            'id': id,
            'nafn': nafn,
            'faedingardagur': faedingardagur,
            'skammstofun': skammstofun,
            'thingflokkur': thingflokkur,
            'thingskjol': thingskjol
        })

    conn.close()
    return entries

def generate_html(entries, template_path, output_path):
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('thingmenn_template.html')
    html_output = template.render(entries=entries)

    with open(output_path, 'w') as f:
        f.write(html_output)

if __name__ == '__main__':
    db_path = os.path.join(os.path.dirname(__file__), '../thing.db')
    entries = fetch_thingmenn_entries(db_path)
    generate_html(entries, os.path.join(os.path.dirname(__file__), '../templates'), os.path.join(os.path.dirname(__file__), '../output/thingmenn.html'))
