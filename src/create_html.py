from jinja2 import Template, Environment, FileSystemLoader
import sqlite3
import os
import get_hagstofa

DB_PATH = os.path.join('db', 'althingi.db')
OUTPUT_PATH = os.path.join('output')
TEMPLATE_PATH = os.path.join('templates')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Function to generate HTML for each table
def generate_html(query, template_file, output_file, context):
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in results]
    
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template(template_file)
    
    output_html = template.render(rows=rows, **context)
    
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    with open(os.path.join(OUTPUT_PATH, output_file), 'w', encoding='utf-8') as f:
        f.write(output_html)

# Queries and files
queries_files = [
    {
        "query": """WITH RankedFlutningsmadur AS (
                        SELECT ts.*, f.nafn AS flutningsmadur_name, f.radherra AS flutningsmadur_radherra,
                        ROW_NUMBER() OVER (PARTITION BY ts.malsnumer ORDER BY f.rada) AS row_num
                        FROM thingskjal ts
                        JOIN flutningsmadur f ON ts.skjalsnumer = f.skjalsnumer
                    )
                    SELECT r.malsnumer, tm.malsheiti, tm.stadamals, m.efnisgreining, r.utbyting,
                    r.skjalategund, tm.nefnd, tm.html, r.flutningsmadur_name, r.flutningsmadur_radherra, tm.thingflokkur
                    FROM RankedFlutningsmadur r
                    JOIN thingmal tm ON r.malsnumer = tm.malnumer
                    JOIN malaskra m ON r.malsnumer = m.malsnumer
                    LEFT JOIN thingmenn tm ON r.flutningsmadur_name = tm.nafn
                    WHERE r.skjalategund IN ('frumvarp', 'þáltill.', 'stjórnarfrumvarp', 'stjórnartillaga', 'frumvarp nefndar')
                    AND r.row_num = 1;""",
        "template_file": 'thingmal_template.html',
        "output_file": 'thingmal.html',
        "context": {'filter': 'none'}
    },
    {
        "query": """SELECT t1.id, t1.skjalsnumer, fm.nafn, t1.malsnumer, tm.html, tm.malsheiti,
                        tm.stadamals, t1.utbyting, t1.skjalategund,
                        CASE WHEN t1.skjalategund = 'svar' THEN t2.utbyting ELSE strftime('%Y-%m-%d', 'now') END AS svar_dagsetning,
                        CASE WHEN t1.skjalategund = 'svar' THEN (julianday(t2.utbyting) - julianday(t1.utbyting)) * 5 / 7
                        ELSE (julianday(strftime('%Y-%m-%d', 'now')) - julianday(t1.utbyting)) * 5 / 7 END AS days_between
                    FROM thingskjal t1
                    LEFT JOIN thingskjal t2 ON t1.malsnumer = t2.malsnumer AND t2.skjalategund = 'svar'
                    JOIN thingmal tm ON t1.malsnumer = tm.malnumer
                    JOIN flutningsmadur fm ON t1.skjalsnumer = fm.skjalsnumer
                    WHERE t1.skjalategund = 'fsp. til skrifl. svars';""",
        "template_file": 'fyrirspurnir_template.html',
        "output_file": 'fyrirspurnir.html',
        "context": {'filter': 'none'}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_tegund = "ft";""",
        "template_file": 'oundirbunar_template.html',
        "output_file": 'raedur_oundirbunar.html',
        "context": {}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_tegund = "st";""",
        "template_file": 'storfin_template.html',
        "output_file": 'raedur_storfin.html',
        "context": {}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_heiti NOT NULL AND raeda_texti != ""
                    ORDER BY id DESC;""",
        "template_file": 'raedur_timarod_template.html',
        "output_file": 'raedur_timarod.html',
        "context": {}
    }
]

# Generate HTML files
for item in queries_files:
    generate_html(item['query'], item['template_file'], item['output_file'], item['context'])

# Special case for Hagstofa data
data, order = get_hagstofa.get_visitala_data()
template_file = 'visitala_template.html'
template = env.get_template(template_file)
output_html = template.render(data=data, order=order)
with open(os.path.join(OUTPUT_PATH, 'gogn_visitala.html'), 'w') as f:
    f.write(output_html)

# Generate index.html
query = """SELECT *, count(d.malsnumer) FROM dagskra d
           JOIN thingskjal ts ON ts.malsnumer = d.malsnumer
           JOIN flutningsmadur f ON f.skjalsnumer = ts.skjalsnumer
           GROUP BY d.malsnumer
           ORDER BY hefst, d.lidur_numer;"""

cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
rows = [dict(zip(columns, row)) for row in results]

template = env.get_template('index_template.html')
output_html = template.render(rows=rows)
with open(os.path.join(OUTPUT_PATH, 'index.html'), 'w') as f:
    f.write(output_html)

conn.close()
