# -*- coding: UTF-8 -*-

import requests
import xmltodict
import sys

session = None
try:
	session = sys.argv[1]
except:
	sys.exit(0)

url = "https://www.althingi.is/altext/xml/thingmalalisti/?lthing="
query = url+str(session)
response = requests.get(query)
#print response.text.encode('utf-8', 'ignore')
data = xmltodict.parse(response.text)

#for k in data[u'málaskrá'][u'mál']:
#	print(k)

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

html_output = "<html><head><script src='https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js'></script></head><body>\n"
html_output += "<script type='text/javascript'>"+script+"</script>\n"
html_output += "<table id='table_issues' border='1'>\n"
html_output += """\t<thead>
\t\t<th data-type='number'>Málsnúmer</th>
\t\t<th data-type='string'>Tegund máls</th>
\t\t<th data-type='string'>Málsheiti</th>
\t</thead>\n"""
html_output += "<tbody>\n"
for k in data[u'málaskrá'][u'mál']:
	html_output += """\t<tr>\n"""
	html_output += "\t\t<td>"+k[u'@málsnúmer']+"</td>\n"
	html_output += "\t\t<td>"+k[u'málstegund'][u'heiti']+"</td>\n"
	html_output += "\t\t<td><a href='"+k[u'html']+"'>"+k[u'málsheiti']+"</a></td>\n"
	html_output += """\t</tr>\n"""

html_output += "</tbody>\n"
html_output += "</table></body></html>"
 
with open("file.html", "w") as file:
	file.write(html_output)
 
