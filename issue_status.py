# -*- coding: UTF-8 -*-

import requests
import xmltodict
import sys, os

session = None
force = False
try:
  session = sys.argv[1]
  if len(sys.argv) > 2:
    force = sys.argv[2]
except:
	sys.exit(0)

url = "https://www.althingi.is/altext/xml/thingmalalisti/?lthing="
query = url+str(session)
response = requests.get(query)
#print response.text.encode('utf-8', 'ignore')
data = xmltodict.parse(response.text)

script = """
$(function() {
  const ths = $("th");
  let sortOrder = 1;

  ths.on("click", function() {
    const rows = sortRows(this);
    rebuildTbody(rows);
    updateClassName(this);
    sortOrder *= -1; //反転
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
      //全て小文字に揃えている。toLowerCase()
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
def cache_or_fetch(url, force=False):
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

def get_flutningsmenn_data(url):
  data = cache_or_fetch(url, force)
  if u'nefnd' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn']:
    try:
      flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'heiti']
    except:
      flutningsmenn = ''
    return flutningsmenn

  try:
    if u'ráðherra' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0]:
      flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'ráðherra']
    else:
      flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'nafn']
  except:
    try:
      if u'ráðherra' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður']:
        flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'ráðherra']
      else:
        flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'nafn']
    except:
      flutningsmenn = ''
  return flutningsmenn

def get_document_data(url):
  data = cache_or_fetch(url, force)
  thingskjal_url = ''
  try:
    issue_status = data[u'þingmál'][u'mál'][u'staðamáls']
  except:
    issue_status = ''
  try:
    try:
      thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][0][u'slóð'][u'xml']
    except:
      thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][u'slóð'][u'xml']
  except:
    return ''
  try:
    if data[u'þingmál'][u'ræður'][u'ræða'][0][u'tegundræðu'] == 'flutningsræða' or data[u'þingmál'][u'ræður'][u'ræða'][1][u'tegundræðu'] == 'flutningsræða':
      issue_introduction = data[u'þingmál'][u'ræður'][u'ræða'][0][u'ræðahófst']
    else:
      issue_introduction = ''
  except Exception as e:
    issue_introduction = ''
  try:
    documents = data[u'þingmál'][u'þingskjöl'][u'þingskjal']
    if type(documents) is list:
      issue_published = documents[0][u'útbýting']
    else:
      issue_published = documents[u'útbýting']
  except:
    issue_published = ''
  return {'mps': get_flutningsmenn_data(thingskjal_url), 'issue_status': issue_status, 'issue_introduction': issue_introduction, 'issue_published': issue_published}

def get_mp_party(url, session):
  data = cache_or_fetch(url, force)
  try:
    if data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þing'] == str(session):
      #print(data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þingflokkur'][u'#text'])
      return data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þingflokkur'][u'#text']
  except Exception as e:
    for session_data in data[u'þingmaður'][u'þingsetur'][u'þingseta']:
      if session_data[u'þing'] == str(session):
        return session_data[u'þingflokkur'][u'#text']
  return None

def get_party_mps(session):
  url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="
  data = cache_or_fetch(url+str(session), force)
  results = {} #{flokkur1: [mp1, mp2], flokkur2: ...}
  for mp in data[u'þingmannalisti'][u'þingmaður']:
    try:
      mp_party = get_mp_party(mp[u'xml'][u'þingseta'], session)
    except:
      mp_party = None
    mp_name = mp[u'nafn']
    if mp_party in results:
      results[mp_party].append(mp_name)
    else:
      results[mp_party] = [mp_name]
  return results

def find_mp_party(mp, parties):
  #print(mp)
  for party in parties:
    if mp in parties[party]:
      return party
  return mp

malstegund = {
  'l': 'Frumvarp til laga', 
  'f': 'Tillaga til þingsályktunar', 
  'm': 'Fyrirspurn',
  'n': 'Álit',
  'b': 'Beiðni um skýrslu',
  'q': 'Fyrirspurn',
  'um': 'sérstök umræða',
  'a': 'Tillaga til þingsályktunar',
  's': 'Skýrsla',
  'ft': 'óundirbúinn fyrirspurnatími'}

print("Collecting party info")
parties = get_party_mps(session)

html_output = "<html><head><script src='https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js'></script></head><body>\n"
html_output += "<script type='text/javascript'>"+script+"</script>\n"
html_output += "<table id='table_issues' border='1'>\n"
html_output += """\t<thead>
\t\t<th data-type='number'>Málsnúmer</th>
\t\t<th data-type='string'>Tegund máls</th>
\t\t<th data-type='string'>Staða máls</th>
\t\t<th data-type='string'>Málsheiti</th>
\t\t<th data-type='string'>Flokkur</th>
\t\t<th data-type='string'>Útbýting</th>
\t</thead>\n"""
html_output += "<tbody>\n"

#Búa til sköl fyrir þingmál (frumvörp og þingsályktanir) - í nefnd, bíður umræðu og samþykkt og svo svaraðar og ósvaraðar fyrirspurnir

committee = html_output
waiting = html_output
asked =html_output
answered = html_output
passed = html_output
government_waiting = html_output
government_committee = html_output

for k in data[u'málaskrá'][u'mál']:
  try:
    document_data = get_document_data(k[u'xml'])
    print(k[u'@málsnúmer'])
    if u'nefnd' in document_data[u'issue_status']:
      flutningur = str(find_mp_party(str(document_data['mps']), parties))
      if 'ráðherra' in flutningur:
        government_committee += """\t<tr>\n"""
        government_committee += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
        government_committee += "\t\t<td>" + k[u'málstegund'][u'heiti'] + "</td>\n"
        government_committee += "\t\t<td>" + str(document_data['issue_status']) +"</td>\n"
        government_committee += "\t\t<td><a href='" + k[u'html'] + "'>" + k[u'málsheiti'] + "</a></td>\n"
        government_committee += "\t\t<td>" + flutningur +"</td>\n"
        government_committee += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
        government_committee += """\t</tr>\n"""
      else:
        committee += """\t<tr>\n"""
        committee += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
        committee += "\t\t<td>" + k[u'málstegund'][u'heiti'] + "</td>\n"
        committee += "\t\t<td>" + str(document_data['issue_status']) +"</td>\n"
        committee += "\t\t<td><a href='" + k[u'html'] +"'>" + k[u'málsheiti'] + "</a></td>\n"
        committee += "\t\t<td>" + flutningur + "</td>\n"
        committee += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
        committee += """\t</tr>\n"""
    elif u'Bíður' in document_data[u'issue_status']:
      #ríkisstjórnarmál eða þingmannamál?
      flutningur = str(find_mp_party(str(document_data['mps']), parties))
      if 'ráðherra' in flutningur:
        government_waiting += """\t<tr>\n"""
        government_waiting += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
        government_waiting += "\t\t<td>" + k[u'málstegund'][u'heiti'] + "</td>\n"
        government_waiting += "\t\t<td>" + str(document_data['issue_status']) + "</td>\n"
        government_waiting += "\t\t<td><a href='" + k[u'html']+"'>" + k[u'málsheiti'] + "</a></td>\n"
        government_waiting += "\t\t<td>" + flutningur + "</td>\n"
        government_waiting += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
        government_waiting += """\t</tr>\n"""    
      else:
        waiting += """\t<tr>\n"""
        waiting += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
        waiting += "\t\t<td>" + k[u'málstegund'][u'heiti'] +"</td>\n"
        waiting += "\t\t<td>" + str(document_data['issue_status']) +"</td>\n"
        waiting += "\t\t<td><a href='" + k[u'html'] + "'>" + k[u'málsheiti'] + "</a></td>\n"
        waiting += "\t\t<td>" + flutningur + "</td>\n"
        waiting += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
        #bæta við hvenær var sent til nefndar
        waiting += """\t</tr>\n"""    
    elif u'var svarað' in document_data[u'issue_status']:
      answered += """\t<tr>\n"""
      answered += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
      answered += "\t\t<td>" + k[u'málstegund'][u'heiti']+"</td>\n"
      answered += "\t\t<td>" + str(document_data['issue_status']) +"</td>\n"
      answered += "\t\t<td><a href='" + k[u'html'] + "'>" + k[u'málsheiti'] + "</a></td>\n"
      answered += "\t\t<td>" + str(find_mp_party(str(document_data['mps']), parties)) + "</td>\n"
      answered += "\t\t<td>" + document_data[u'issue_published']+"</td>\n"
      #bæta við hvað tók langan tíma að svara
      answered += """\t</tr>\n"""
    elif u'ekki verið svarað' in document_data[u'issue_status']:
      asked += """\t<tr>\n"""
      asked += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
      asked += "\t\t<td>" + k[u'málstegund'][u'heiti'] + "</td>\n"
      asked += "\t\t<td>" + str(document_data['issue_status']) + "</td>\n"
      asked += "\t\t<td><a href='" + k[u'html'] + "'>" + k[u'málsheiti'] + "</a></td>\n"
      asked += "\t\t<td>" + str(find_mp_party(str(document_data['mps']), parties)) + "</td>\n"
      asked += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
      #bæta við fjöldi daga síðan var spurt
      asked += """\t</tr>\n"""
    elif u'Samþykkt' in document_data[u'issue_status']:
      passed += """\t<tr>\n"""
      passed += "\t\t<td>" + k[u'@málsnúmer'] + "</td>\n"
      passed += "\t\t<td>" + k[u'málstegund'][u'heiti'] + "</td>\n"
      passed += "\t\t<td>" + str(document_data['issue_status']) + "</td>\n"
      passed += "\t\t<td><a href='" + k[u'html'] + "'>" + k[u'málsheiti'] + "</a></td>\n"
      passed += "\t\t<td>" + str(find_mp_party(str(document_data['mps']), parties)) + "</td>\n"
      passed += "\t\t<td>" + document_data[u'issue_published'] + "</td>\n"
      passed += """\t</tr>\n"""
  except:
    pass

html_footer = "</tbody>\n"
html_footer += "</table></body></html>"
committee += html_footer
waiting += html_footer
asked += html_footer
answered += html_footer
passed += html_footer
government_waiting += html_footer

with open("in_committee.html", "w") as file:
  file.write(committee)
with open("waiting.html", "w") as file:
  file.write(waiting)
with open("asked.html", "w") as file:
  file.write(asked)
with open("answered.html", "w") as file:
  file.write(answered)
with open("passed.html", "w") as file:
  file.write(passed)
with open("government_waiting.html", "w") as file:
  file.write(government_waiting)
with open("government_committee.html", "w") as file:
  file.write(government_committee)
