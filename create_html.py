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
    r.skjalategund IN ('frumvarp', 'þáltill.', 'stjórnarfrumvarp', 'stjórnartillaga', 'frumvarp nefndar')
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
    "nefndir_AMN.html": "Allsherjar- og menntamálanefnd",
    "nefndir_ATV.html": "Atvinnuveganefnd",
    "nefndir_EVN.html": "Efnahags- og viðskiptanefnd",
    "nefndir_FLN.html": "Fjárlaganefnd",
    "nefndir_SEN.html": "Stjórnskipunar- og eftirlitsnefnd",
    "nefndir_UMS.html": "Umhverfis- og samgöngunefnd",
    "nefndir_UTN.html": "Utanríkismálanefnd",
    "nefndir_VEL.html": "Velferðarnefnd",
    "nefndir_FRA.html": "Framtíðarnefnd",
    "raedur_oundirbunar.html": "Óundirbúnar fyrirspurnir",
    "raedur_storfin.html": "Störf þingsins",
    "raedur_timarod.html": "Tímaröð",
    "raedur_skrar.html": "Ræðuskrár",
    "gogn_visitala.html": "Vísitala neysluverðs",
    "gogn_thjodhagsspa.html": "Þjóðhagsspá"
    # Add more entries as needed
}

# Group files by categories
categories = {
    "Ríkisstjórnarmál": [f for f in filtered_files if "thingmal_rikisstjorn" in f.lower()],
    "Þingmannamál": [f for f in filtered_files if "thingmal_thingmannamal" in f.lower()],
    "Nefndir": [f for f in filtered_files if "nefndir" in f.lower()],
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

template_file = 'nefndir_template.html'
env = Environment(loader=FileSystemLoader('.'))  # Adjust the loader path accordingly
# Load the template
template = env.get_template(template_file)

nefnd_alias = {
    "AMN": "Allsherjar- og menntamálanefnd",
    "ATV": "Atvinnuveganefnd",
    "EVN": "Efnahags- og viðskiptanefnd",
    "FLN": "Fjárlaganefnd",
    "SEN": "Stjórnskipunar- og eftirlitsnefnd",
    "UMS": "Umhverfis- og samgöngunefnd",
    "UTN": "Utanríkismálanefnd",
    "VEL": "Velferðarnefnd",
    "FRA": "Framtíðarnefnd"
}
output_html = template.render(rows=rows, filter='AMN', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_AMN.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='ATV', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_ATV.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='EVN', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_EVN.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='FLN', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_FLN.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='SEN', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_SEN.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='UMS', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_UMS.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='UTN', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_UTN.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='VEL', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_VEL.html', 'w') as f:
    f.write(output_html)
output_html = template.render(rows=rows, filter='FRA', nefnd_alias=nefnd_alias, categories=categories, aliases=aliases)
with open('nefndir_FRA.html', 'w') as f:
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

#Ná í ræður í tímaröð, mínus forsetaræður og ræður þar sem ræðutexti er ekki tilbúinn
query = """select r.*, tm.* from raedur r
join thingmenn tm on r.raedumadur = tm.nafn
where mal_heiti NOT NULL and raeda_texti != ""
order by id DESC"""
cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
rows = [dict(zip(columns, row)) for row in results]

# Render the template with the query results
output_html = template.render(rows=rows, categories=categories, aliases=aliases)
with open('raedur_timarod.html', 'w') as f:
    f.write(output_html)

query = """select * from thingmenn"""
cursor.execute(query)
results = cursor.fetchall()
columns = [column[0] for column in cursor.description]
# Convert the list of tuples to a list of dictionaries
data = [dict(zip(columns, row)) for row in results]

# Create an empty set to track unique pairs
unique_pairs = set()

# Create an empty list for the final output
unique_values_list = []

# Extracting unique 'nafn'
unique_nafn = set(item['nafn'] for item in data)

# Extracting unique 'thingflokkur'
unique_thingflokkur = set(item['thingflokkur'] for item in data)

# Iterate through the original list
for item in data:
    # Create a tuple of (nafn, thingflokkur)
    pair = (item['nafn'], item['thingflokkur'])
    # Add the pair to the list and set if it's not already there
    if pair not in unique_pairs:
        unique_pairs.add(pair)
        unique_values_list.append({'nafn': item['nafn'], 'thingflokkur': item['thingflokkur']})

# Check for folder
folder_path = 'raedur/'
if not os.path.exists(folder_path):
    # If the folder does not exist, create it
    os.makedirs(folder_path)

# Create files with raedur for each thingflokkur and each nafn
for flokkur in unique_thingflokkur:
    #loop through rows to find all raedur from flokkur
    raedur_flokks = ''
    for r in rows:
        if r['thingflokkur'] == flokkur:
            raedur_flokks += 'Ræðumaður: ' + r['raedumadur'] + '\n'
            raedur_flokks += r['raeda_texti'] + '\n\n'
    with open('raedur/'+flokkur+'.txt', 'w') as f:
        f.write(raedur_flokks)

for nafn in unique_nafn:
    #loop through rows to find all raedur from nafn
    raedur_thingmanns = ''
    for r in rows:
        if r['nafn'] == nafn:
            raedur_thingmanns += r['raeda_texti'] + '\n###\n'
    with open('raedur/'+nafn+'.txt', 'w') as f:
        f.write(raedur_thingmanns)

# Specify the template file and create a Jinja2 environment
template_file = 'raedur_skrar_template.html'
template = env.get_template(template_file)
output_html = template.render(
        rows=rows, categories=categories, aliases=aliases, 
        thingmenn=unique_nafn, 
        thingflokkar=unique_thingflokkur, 
        nafn_thingflokkur=unique_values_list
    )
with open('raedur_timarod.html', 'w') as f:
    f.write(output_html)

#Hagstofugögn
template_file = 'visitala_template.html'
template = env.get_template(template_file)
data, order = get_hagstofa.get_visitala_data()
output_html = template.render(data=data, order=order, categories=categories, aliases=aliases)
with open('gogn_visitala.html', 'w') as f:
    f.write(output_html)

""" Í VINNSLU
thjodhagsspa_rows = {
0: "Einkaneysla",
1: "Samneysla",
2: "Fjármunamyndun",
3: "Atvinnuvegafjárfesting",
4: "Fjárfesting í íbúðarhúsnæði",
5: "Fjárfesting hins opinbera",
6: "Þjóðarútgjöld, alls",
7: "Útflutningur vöru og þjónustu",
8: "Innflutningur vöru og þjónustu",
9: "Verg landsframleiðsla",
10: "Vöru- og þjónustujöfnuður, % af VLF",
11: "Viðskiptajöfnuður, % af VLF",
12: "Viðskiptajöfnuður án innlánsstofnana í slitameðferð, % af VLF",
13: "VLF á verðlagi hvers árs",
14: "Vísitala neysluverðs",
15: "Gengisvísitala",
16: "Raungengi",
17: "Atvinnuleysi, % af vinnuafli",
18: "Kaupmáttur launa",
19: "Hagvöxtur í helstu viðskiptalöndum",
20: "Alþjóðleg verðbólga",
21: "Verð útflutts áls",
22: "Olíuverð"
}
template_file = 'thjodhagsspa_template.html'
template = env.get_template(template_file)
data = get_hagstofa.get_thjodhagsspa_data()
output_html = template.render(data=data, row_labels=thjodhagsspa_rows, categories=categories, aliases=aliases)
with open('gogn_thjodhagsspa.html', 'w') as f:
    f.write(output_html)
"""

#create index file
#dagskrá þingsins
query = """SELECT *, count(d.malsnumer) FROM dagskra d
join thingskjal ts on ts.malsnumer = d.malsnumer
join flutningsmadur f on f.skjalsnumer = ts.skjalsnumer
group by d.malsnumer
order by hefst, d.lidur_numer
"""

cursor.execute(query)
results = cursor.fetchall()
try:
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
except:
    # Búa til tóman þingfund
    output = template.render(categories=categories, rows=[], aliases=aliases)
    with open("index.html", "w") as index_file:
        index_file.write(output)

conn.close()
