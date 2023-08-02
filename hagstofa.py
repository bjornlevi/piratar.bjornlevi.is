# -*- coding: utf-8 -*-

import requests
from datetime import datetime as dt
import json
import pandas as pd

url = 'https://px.hagstofa.is:443/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/2_undirvisitolur/VIS01304.px'
headers = {
    'Content-Type': 'application/json',
}

nr_months = 15

#prepare the months to retrieve starting with last month (current month will not be available)
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
m = (dt.now().month-2) #month index: month-1 and index -1. If current month is 1 the last month is 12 at index in the months array.
y = dt.now().year
if dt.now().month == 1: #if it's january, starting year needs to be last year
    y -= 1

query_months = []
for i in range(nr_months):
    query_months.insert(0, str(y)+"M"+months[m])
    m -= 1
    if months[m] == "12":
        y -= 1


query = {
  "query": [
    {
      "code": "Mánuður",
      "selection": {
        "filter": "item",
        "values": query_months
      }
    },
    {
      "code": "Undirvísitala",
      "selection": {
        "filter": "item",
        "values": [
          "IS00",
          "IS01",
          "IS02",
          "IS03",
          "IS04",
          "IS041",
          "IS042",
          "IS0451",
          "IS0455",
          "IS05",
          "IS06",
          "IS07",
          "IS0722"
        ]
      }
    }
  ],
  "response": {
    "format": "json"
  }
}

flokkar = {
    "IS00": "Vísitala neysluverðs",
    "IS01": "Matur og drykkjarvara",
    "IS02": "Áfengi og tóbak",
    "IS03": "Föt og skór",
    "IS04": "Húsnæði, hiti og rafmagn",
    "IS041": "Greidd húsaleiga",
    "IS042": "Reiknuð húsaleiga",
    "IS0451": "Rafmagn",
    "IS0455": "Hiti",    
    "IS05": "Húsgögn og heimilisbúnaður",
    "IS06": "Heilsa",
    "IS07": "Ferðir og flutningar",
    "IS0722": "Bensín og olíur"
}

def create_html_table(data):
    html = "<table>\n"
    
    # Add table header
    html += "<tr>"
    html+= "<th>Mánuður</th>"
    for k in data.keys():
        html += "<th>"+k+"</th>"
    html += "</tr>\n"

    # Add table rows
    df = pd.DataFrame(data)

    html += "</table>"
    return html

response = requests.post(url, headers=headers, json=query)
#query['response']['format'] = "px"
#meta_response = requests.post(url, headers=headers, json=query)
data = ''

if response.status_code == 200:
    # The request was successful
    data = response.text
    #json_data = meta_response.text
else:
    # The request failed
    print(f'Request failed with status code {response.status_code}')

data = json.loads(data.strip('\ufeff'))

table = {
    'month': []
} #collect the data for each category in the form {'month': 'value'}

for d in data['data']:
    #d = {'key': ['2022M02', 'IS04'], 'values': ['208.8']}
    #table = {'months': ['2022M02', '2022M03', ...'], 'IS04': ['value1', 'value2', ...]}
    if d['key'][0] not in table['month']:
        table['month'].append(d['key'][0])

    if d['key'][1] not in table.keys():
        table[d['key'][1]] = []
    table[d['key'][1]].append(d['values'][0])

# Create a new dictionary with the updated keys
table = {flokkar.get(key, key): value for key, value in table.items()}

delta_breytingar = { #Need to make new columns to show the monthly changes
    "Vísitala neysluverðs":         "IS00 Δ",
    "Matur og drykkjarvara":        "IS01 Δ",
    "Áfengi og tóbak":              "IS02 Δ",
    "Föt og skór":                  "IS03 Δ",
    "Húsnæði, hiti og rafmagn":     "IS04 Δ",
    "Greidd húsaleiga":             "IS041 Δ",
    "Reiknuð húsaleiga":            "IS042 Δ",
    "Rafmagn":                      "IS0451 Δ",
    "Hiti":                         "IS0455 Δ",
    "Húsgögn og heimilisbúnaður":   "IS05 Δ",
    "Heilsa":                       "IS06 Δ",
    "Ferðir og flutningar":         "IS07 Δ",
    "Bensín og olíur":              "IS0722 Δ"
}

for k in delta_breytingar:
    # Convert the elements in the list to float values
    data_list_float = [float(val) for val in table[k]]

    # Calculate the percentage difference for each element
    percentage_diff_list = [None] + [data_list_float[i] / data_list_float[i - 1] if i > 0 else None for i in range(1, len(data_list_float))]

    table[delta_breytingar[k]] = percentage_diff_list

# Define the desired column order
desired_column_order = [
    'month', 
    "Vísitala neysluverðs",
    "IS00 Δ",
    "Matur og drykkjarvara",
    "IS01 Δ",
    "Áfengi og tóbak",
    "IS02 Δ",
    "Föt og skór",
    "IS03 Δ",
    "Húsnæði, hiti og rafmagn",
    "IS04 Δ",
    "Greidd húsaleiga",
    "IS041 Δ",
    "Reiknuð húsaleiga",
    "IS042 Δ",
    "Rafmagn",
    "IS0451 Δ",
    "Hiti",    
    "IS0455 Δ",
    "Húsgögn og heimilisbúnaður",
    "IS05 Δ",
    "Heilsa",
    "IS06 Δ",
    "Ferðir og flutningar",
    "IS07 Δ",
    "Bensín og olíur", 
    "IS0722 Δ"
] 

# Convert the dictionary to a pandas DataFrame
df = pd.DataFrame(table)

# Reorder the columns in the DataFrame
df = df[desired_column_order]

# Convert the DataFrame to an HTML table
html_table = df.to_html(index=False)

# Create the full HTML content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Þróun vísitölu</title>
</head>
<body>
    <h2>Þróun vísitölu sl. árs</h2>
    {html_table}
</body>
</html>
"""

# Save the HTML content to a file
with open('visitala.html', 'w') as file:
    file.write(html_content)
