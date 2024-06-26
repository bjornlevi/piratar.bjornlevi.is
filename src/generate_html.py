# generate_html.py

import sqlite3
import os
from jinja2 import Environment, FileSystemLoader
import get_hagstofa
from config_html import aliases, categories, nefnd_alias, queries_files

def render_template(template_file, output_file, context):
    try:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(template_file)
        output_html = template.render(context)

        output_path = os.path.join('output', output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(output_html)
        print(f"Generated {output_file} successfully.")
    except Exception as e:
        print(f"Error rendering {template_file}: {e}")

def main():
    conn = sqlite3.connect('db/althingi.db')
    cursor = conn.cursor()

    for query_info in queries_files:
        cursor.execute(query_info["query"])
        results = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in results]
        context = query_info["context"]
        context.update({
            'rows': rows,
            'categories': categories,
            'aliases': aliases,
            'nefnd_alias': nefnd_alias
        })

        # Determine subfolder based on file name pattern
        file_name = query_info["output_file"]
        if "_" in file_name:
            subfolder = file_name.split("_")[0]
            output_file = os.path.join(subfolder, file_name)
        else:
            output_file = file_name

        render_template(query_info["template_file"], output_file, context)

    # Additional templates without SQL queries
    hagstofa_data, order = get_hagstofa.get_visitala_data()
    render_template('visitala_template.html', 'gogn/gogn_visitala.html', {
        'data': hagstofa_data,
        'order': order,
        'categories': categories,
        'aliases': aliases
    })

    # Create index file
    query = """SELECT *, count(d.malsnumer) FROM dagskra d
               JOIN thingskjal ts ON ts.malsnumer = d.malsnumer
               JOIN flutningsmadur f ON f.skjalsnumer = ts.skjalsnumer
               GROUP BY d.malsnumer
               ORDER BY hefst, d.lidur_numer"""
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in results]

    try:
        render_template("index_template.html", "index.html", {
            'categories': categories,
            'rows': rows,
            'aliases': aliases
        })
    except Exception as e:
        render_template("index_template.html", "index.html", {
            'categories': categories,
            'rows': [],
            'aliases': aliases
        })

    conn.close()

if __name__ == '__main__':
    main()
