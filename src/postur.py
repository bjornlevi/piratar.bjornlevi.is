# -*- coding: UTF-8 -*-

import requests
import xmltodict
from datetime import datetime
import sys, os

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

#{'þingmaður': 
#{
#	'@id': '1270', 
#	'nafn': 'Þórhildur Sunna Ævarsdóttir', 
#	'fæðingardagur': '1987-05-06', 
#	'facebook': 'https://www.facebook.com/sunnapirati', 
# 	'twitter': 'https://twitter.com/sunnago', 
#	'netfang': {'nafn': 'thorhildursunna', 'lén': 'althingi.is'}, 
#	'xml': {'lífshlaup': 'https://www.althingi.is/altext/xml/thingmenn/thingmadur/lifshlaup/?nr=1270', 'hagsmunir': 'https://www.althingi.is/altext/xml/thingmenn/thingmadur/hagsmunir/?nr=1270', 'þingseta': 'https://www.althingi.is/altext/xml/thingmenn/thingmadur/thingseta/?nr=1270', 'nefndaseta': 'https://www.althingi.is/altext/xml/thingmenn/thingmadur/nefndaseta/?nr=1270'}, 'html': {'lífshlaup': 'https://www.althingi.is/altext/cv/?nfaerslunr=1270', 'hagsmunir': 'https://www.althingi.is/altext/hagsmunir/?faerslunr=1270', 'þingstörf': 'https://www.althingi.is/vefur/thmstorf.html?nfaerslunr=1270'}}
#}  
def get_mp_details(url):
  data = cache_or_fetch(url, force)
  return data

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
    mp_details = get_mp_details(mp[u'xml'][u'nánar'])
    try:
    	mp_email = mp_details[u'þingmaður'][u'netfang'][u'nafn']+'@'+mp_details[u'þingmaður'][u'netfang'][u'lén']
    except:
    	mp_email = None
    if mp_party in results:
      results[mp_party].append([mp_name, mp_email])
    else:
      results[mp_party] = [[mp_name, mp_email]]
  return results

def collect_all_emails(parties):
	emails = []
	for party in parties:
		emails.append(', '.join([str(e[1]) for e in parties[party] if e[1] is not None]))

	return emails


parties = get_party_mps(session)

html_output = """
<html><head><title>Sendu þingmönnum póst</title></head><body>
<h2>Sendu þingmönnum póst</h2>
<p>Sendu öllum þingmönnum póst: """

print(collect_all_emails(parties))