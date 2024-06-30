import os
import requests
import xmltodict

def cache_file(url, contents):
    file_name = "cache/" + url.replace('/', '-')
    with open(file_name, "w") as f:
        f.write(contents)

def get_xml_data(url):
    response = requests.get(url)
    cache_file(url, response.text)
    return xmltodict.parse(response.text)

def cache_or_fetch(url, force):
    os.makedirs("cache", exist_ok=True)
    file_name = "cache/" + url.replace('/', '-')

    if force or not os.path.exists(file_name):
        return get_xml_data(url)
    else:
        with open(file_name, "r") as f:
            return xmltodict.parse(f.read())
