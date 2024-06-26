import sqlite3
import os
from jinja2 import Environment, FileSystemLoader

# Constants
DB_PATH = os.path.join('db', 'althingi.db')
OUTPUT_PATH = os.path.join('output')
TEMPLATE_PATH = os.path.join('templates')

# Database connection
def connect_db():
    return sqlite3.connect(DB_PATH)

# Jinja2 environment setup
def create_env():
    return Environment(loader=FileSystemLoader(TEMPLATE_PATH))

# Define categories and aliases
categories = {
    "Ríkisstjórnarmál": ["thingmal_rikisstjorn_bida_umraedu", "thingmal_rikisstjorn_i_nefnd", "thingmal_rikisstjorn_samthykkt"],
    "Þingmannamál": ["thingmal_thingmannamal_bida_umraedu", "thingmal_thingmannamal_i_nefnd", "thingmal_thingmannamal_samthykkt"],
    "Nefndir": ["nefndir_AMN", "nefndir_ATV", "nefndir_EVN", "nefndir_FLN", "nefndir_SEN", "nefndir_UMS", "nefndir_UTN", "nefndir_VEL", "nefndir_FRA"],
    "Fyrirspurnir": ["fyrirspurnir_svarad", "fyrirspurnir_osvarad"],
    "Ræður": ["raedur_oundirbunar", "raedur_storfin", "raedur_timarod"],
    "Gögn": ["gogn_visitala", "gogn_thjodhagsspa"]
}

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
}

# Ensure output path exists
os.makedirs(OUTPUT_PATH, exist_ok=True)
