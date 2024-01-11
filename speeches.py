# -*- coding: utf-8 -*-

import requests
import xmltodict
import sys, os
from string import Template

session = None
force = False
try:
  session = sys.argv[1]
  if len(sys.argv) > 2:
    if sys.argv[2] == "True":
      force = True
except:
	sys.exit(0)

def cache_file(url, contents):
  file_name = "cache/"+url.replace('/','-')
  with open(file_name, "w") as f:
     f.write(contents)

def get_xml_data(url):
  #get new files
  response = requests.get(url)
  #cache file
  cache_file(url, response.text)
  return xmltodict.parse(response.text)

#functions
def cache_or_fetch(url, force):
  try: 
    os.mkdir("cache")
  except:
    pass

  file_name = "cache/"+url.replace('/','-')

  if force:
    return get_xml_data(url)
  else:
    if os.path.exists(file_name):
      #file exists, return file contents
      with open(file_name, "r") as f:
        return xmltodict.parse(f.read())
    else:
      return get_xml_data(url)

url = "https://www.althingi.is/altext/xml/raedulisti/?lthing="
query = url+str(session)

data = cache_or_fetch(query, force)

storfin = []
unprepared = []

tegundir_r = set()
for r in data[u'ræðulisti'][u'ræða']:
	if r[u'mál']['málsheiti'] == u'Störf þingsins':
		storfin.append(r)
	elif r[u'mál']['málsheiti'] == u'Óundirbúinn fyrirspurnatími':
		unprepared.append(r)

script = """
$(function() {
  var file_name = location.href.split("/").slice(-1);

  const ths = $("th");
  let sortOrder = 1;

  ths.on("click", function() {
    const rows = sortRows(this);
    rebuildTbody(rows);
    updateClassName(this);
    sortOrder *= -1; 
  })

  function sortRows(th) {
    const rows = $.makeArray($('tbody > tr'));
    const col = th.cellIndex;
    const type = th.dataset.type;
    rows.sort(function(a, b) {
      return compare(a, b, col, type) * sortOrder;      
    });
    return rows;
  }

  function compare(a, b, col, type) {
    let _a = a.children[col].textContent;
    let _b = b.children[col].textContent;
    if (type === "number") {
      _a *= 1;
      _b *= 1;
    } else if (type === "string") {
      _a = _a.toLowerCase();
      _b = _b.toLowerCase();
    }

    if (_a < _b) {
      return -1;
    }
    if (_a > _b) {
      return 1;
    }
    return 0;
  }

  function rebuildTbody(rows) {
    const tbody = $("tbody");
    while (tbody.firstChild) {
      tbody.remove(tbody.firstChild);
    }

    let j;
    for (j=0; j<rows.length; j++) {
      tbody.append(rows[j]);
    }
  }

  function updateClassName(th) {
    let k;
    for (k=0; k<ths.length; k++) {
      ths[k].className = "";
    }
    th.className = sortOrder === 1 ? "asc" : "desc";   
  }
  
});
"""

html_template = Template("""
<html>
<head>
	<title>Ræður</title>
	<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js'></script>
</head>
<body>
	<script type='text/javascript'>$script</script>
	<table id='table_speeches' border='1'>
		<thead>
			<th data-type='number'>Málsnúmer</th>
			<th data-type='string'>Dagsetning</th>
			<th data-type='string'>Ræðumaður</th>
		</thead>
		$content
	</table>
</body>
</html>
""")

'''
{
	'ræðumaður': 
		{
		'@id': '1422', 
		'nafn': 'Guðbrandur Einarsson', 
		'nánar': 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/?nr=1422'
		}, 
	'dagur': '15.12.2023', 
	'löggjafarþing': '154', 
	'fundur': '51', 
	'ræðahófst': '2023-12-15T11:59:52', 
	'ræðulauk': '2023-12-15T12:02:03', 
	'tegundræðu': 'ræða', 
	'umræða': '*', 
	'mál': 
		{
		'málsflokkur': 'B', 
		'málsnúmer': '490', 
		'málsheiti': 'Störf þingsins', 
		'slóðir': 
			{
			'xml': 'http://www.althingi.is/altext/xml/thingmalalisti/bmal/?lthing=154&malnr=490'
			}
		}, 
	'slóðir': 
		{
		'hljóð': 'http://www.althingi.is/raedur/play.mp3?start=2023-12-15T11:59:52&end=2023-12-15T12:02:03', 
		'xml': 'http://www.althingi.is/xml/154/raedur/rad20231215T115952.xml', 
		'html': 'http://www.althingi.is/altext/raeda/154/rad20231215T115952.html'
		}
}
'''

content_template = Template("""
<tr>
	<td>$mnr</td>
	<td>$dags</td>
	<td>$speaker</td>
</tr>
""")

content = ""
for s in storfin:
	#substitute $mrn, $dags, $speaker
	link = Template("<a href='$link'>$nafn</a>").safe_substitute(link=s[u'slóðir'][u'html'], nafn=s[u'ræðumaður'][u'nafn'])
	try:
		content += content_template.substitute(mnr=s[u'mál'][u'málsnúmer'], dags=s[u'ræðahófst'], speaker=link)
	except:
		print(s)

html_contents = html_template.substitute(content=content, script=script)

with open("storfin.html", "w") as file:
  file.write(html_contents)