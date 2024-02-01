from jinja2 import Template, Environment, FileSystemLoader
import sqlite3, os
import get_hagstofa

conn = sqlite3.connect('thing.db')
cursor = conn.cursor()

# Búa til html um þingskjöl
query = """WITH RankedFlutningsmadur AS (
    SELECT
        ts.*,
        f.nafn AS flutningsmadur_name,
        f.radherra AS flutningsmadur_radherra,
        ROW_NUMBER() OVER (PARTITION BY ts.malsnumer ORDER BY f.rada) AS row_num
    FROM
        thingskjal ts
    JOIN
        flutningsmadur f ON ts.skjalsnumer = f.skjalsnumer
)
SELECT
    r.malsnumer,
    tm.malsheiti,
    tm.stadamals,
    m.efnisgreining,
    r.utbyting,
    r.skjalategund,
    tm.nefnd,
    tm.html,
    r.flutningsmadur_name,
    r.flutningsmadur_radherra,
    tm.thingflokkur
FROM
    RankedFlutningsmadur r
JOIN
    thingmal tm ON r.malsnumer = tm.malnumer
JOIN malaskra m ON r.malsnumer = m.malsnumer
LEFT JOIN
    thingmenn tm ON r.flutningsmadur_name = tm.nafn
WHERE
    r.skjalategund IN ('frumvarp', 'þáltill.', 'stjórnarfrumvarp', 'stjórnartillaga')
    AND r.row_num = 1;"""

#Prepare navigation
# Directory containing HTML files
html_directory = "./"

# List all HTML files in the directory
html_files = [f for f in os.listdir(html_directory) if f.endswith(".html")]

# Filter out files containing "template" in their name
filtered_files = [f for f in html_files if "template" not in f.lower()]

aliases = {
    "fyrirspurnir_svarad.html": "Svaraðar fyrirspurnir",
    "fyrirspurnir_osvarad.html": "Ósvaraðar fyrirspurnir",
    "thingmal_rikisstjorn_bida_umraedu.html": "Bíða umræðu",
    "thingmal_rikisstjorn_i_nefnd.html": "Í nefnd",
    "thingmal_rikisstjorn_samthykkt.html": "Samþykkt",
    "thingmal_thingmannamal_bida_umraedu.html": "Bíða umræðu",
    "thingmal_thingmannamal_i_nefnd.html": "Í nefnd",
    "thingmal_thingmannamal_samthykkt.html": "Samþykkt",
    "raedur_oundirbunar.html": "Óundirbúnar fyrirspurnir",
    "raedur_storfin.html": "Störf þingsins",
    "gogn_visitala.html": "Vísitala neysluverðs"
    # Add more entries as needed
}

# Group files by categories
categories = {
    "Ríkisstjórnarmál": [f for f in filtered_files if "thingmal_rikisstjorn" in f.lower()],
    "Þingmannamál": [f for f in filtered_files if "thingmal_thingmannamal" in f.lower()],
    "Fyrirspurnir": [f for f in filtered_files if "fyrirspurnir" in f.lower()],
    "Ræður": [f for f in filtered_files if "raedur" in f.lower()],
    "Gögn": [f for f in filtered_files if "gogn" in f.lower()],
}


cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Specify the template file and create a Jinja2 environment
template_file = 'thingmal_template.html'
env = Environment(loader=FileSystemLoader('.'))  # Adjust the loader path accordingly

# Load the template
template = env.get_template(template_file)

# Render the template with the query result
output_html = template.render(rows=rows, filter='rikisstjorn_samþykkt', categories=categories, aliases=aliases)
# Write the output to an HTML file
with open('thingmal_rikisstjorn_samthykkt.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='rikisstjorn_i_nefnd', categories=categories, aliases=aliases)
with open('thingmal_rikisstjorn_i_nefnd.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='rikisstjorn_bida_umraedu', categories=categories, aliases=aliases)
with open('thingmal_rikisstjorn_bida_umraedu.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='thingmannamal_bida_umraedu', categories=categories, aliases=aliases)
with open('thingmal_thingmannamal_bida_umraedu.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='thingmannamal_i_nefnd', categories=categories, aliases=aliases)
with open('thingmal_thingmannamal_i_nefnd.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='thingmannamal_samthykkt', categories=categories, aliases=aliases)
with open('thingmal_thingmannamal_samthykkt.html', 'w') as f:
    f.write(output_html)

output_html = template.render(rows=rows, filter='none', categories=categories, aliases=aliases)
with open('thingmal.html', 'w') as f:
    f.write(output_html)

print("Upplýsingar um þingskjöl tilbúin")

#Búa til html um fyrirspurnir
query = """SELECT
    t1.id,
    t1.skjalsnumer,
    fm.nafn,
    t1.malsnumer,
    tm.html,
    tm.malsheiti,
    tm.stadamals,
    t1.utbyting,
    t1.skjalategund,
    CASE
        WHEN t1.skjalategund = 'svar' THEN t2.utbyting
        ELSE strftime('%Y-%m-%d', 'now')
    END AS svar_dagsetning,
    CASE
        WHEN t1.skjalategund = 'svar' THEN (julianday(t2.utbyting) - julianday(t1.utbyting)) * 5 / 7
        ELSE (julianday(strftime('%Y-%m-%d', 'now')) - julianday(t1.utbyting)) * 5 / 7
    END AS days_between
FROM
    thingskjal t1
LEFT JOIN
    thingskjal t2 ON t1.malsnumer = t2.malsnumer AND t2.skjalategund = 'svar'
JOIN
    thingmal tm ON t1.malsnumer = tm.malnumer
JOIN
    flutningsmadur fm ON t1.skjalsnumer = fm.skjalsnumer
WHERE
    t1.skjalategund = 'fsp. til skrifl. svars';"""

cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Specify the template file and create a Jinja2 environment
template_file = 'fyrirspurnir_template.html'
template = env.get_template(template_file)

# Render the template with the query results
output_html = template.render(filter="osvarad",rows=rows, categories=categories, aliases=aliases)
with open('fyrirspurnir_osvarad.html', 'w') as f:
    f.write(output_html)

output_html = template.render(filter="svarad", rows=rows, categories=categories, aliases=aliases)
with open('fyrirspurnir_svarad.html', 'w') as f:
    f.write(output_html)

#Búa til html fyrir ræður. Óundirbúnar og störfin
query = """select r.*, tm.* from raedur r
join thingmenn tm on r.raedumadur = tm.nafn
where mal_tegund = "ft"
"""
cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Specify the template file and create a Jinja2 environment
template_file = 'oundirbunar_template.html'
template = env.get_template(template_file)

# Render the template with the query results
output_html = template.render(rows=rows, categories=categories, aliases=aliases)
with open('raedur_oundirbunar.html', 'w') as f:
    f.write(output_html)

query = """select r.*, tm.* from raedur r
join thingmenn tm on r.raedumadur = tm.nafn
where mal_tegund = "st"
"""
cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Specify the template file and create a Jinja2 environment
template_file = 'storfin_template.html'
template = env.get_template(template_file)

# Render the template with the query results
output_html = template.render(rows=rows, categories=categories, aliases=aliases)
with open('raedur_storfin.html', 'w') as f:
    f.write(output_html)

#Hagstofugögn
template_file = 'visitala_template.html'
template = env.get_template(template_file)
data, order = get_hagstofa.get_visitala_data()
output_html = template.render(data=data, order=order, categories=categories, aliases=aliases)
with open('gogn_visitala.html', 'w') as f:
    f.write(output_html)

#create index file
#dagskrá þingsins
query = """SELECT *, count(d.malsnumer) FROM dagskra d
join thingskjal ts on ts.malsnumer = d.malsnumer
join flutningsmadur f on f.skjalsnumer = ts.skjalsnumer
group by d.malsnumer
order by d.lidur_numer
"""

cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Jinja2 template for index.html
template_loader = FileSystemLoader(searchpath="./")
template_env = Environment(loader=template_loader)
template = template_env.get_template("index_template.html")

# Generate index.html
output = template.render(categories=categories, rows=rows, aliases=aliases)
with open("index.html", "w") as index_file:
    index_file.write(output)

conn.close()
