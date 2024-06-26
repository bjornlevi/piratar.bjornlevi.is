# config.py

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
}

categories = {
    "Ríkisstjórnarmál": ["thingmal_rikisstjorn_bida_umraedu.html", "thingmal_rikisstjorn_i_nefnd.html", "thingmal_rikisstjorn_samthykkt.html"],
    "Þingmannamál": ["thingmal_thingmannamal_bida_umraedu.html", "thingmal_thingmannamal_i_nefnd.html", "thingmal_thingmannamal_samthykkt.html"],
    "Nefndir": ["nefndir_AMN.html", "nefndir_ATV.html", "nefndir_EVN.html", "nefndir_FLN.html", "nefndir_SEN.html", "nefndir_UMS.html", "nefndir_UTN.html", "nefndir_VEL.html", "nefndir_FRA.html"],
    "Fyrirspurnir": ["fyrirspurnir_svarad.html", "fyrirspurnir_osvarad.html"],
    "Ræður": ["raedur_oundirbunar.html", "raedur_storfin.html", "raedur_timarod.html"],
    "Gögn": ["gogn_visitala.html"]
}

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

queries_files = [
    {
        "query": """WITH RankedFlutningsmadur AS (
                        SELECT ts.*, f.nafn AS flutningsmadur_name, f.radherra AS flutningsmadur_radherra,
                        ROW_NUMBER() OVER (PARTITION BY ts.malsnumer ORDER BY f.rada) AS row_num
                        FROM thingskjal ts
                        JOIN flutningsmadur f ON ts.skjalsnumer = f.skjalsnumer
                    )
                    SELECT r.malsnumer, tm.malsheiti, tm.stadamals, m.efnisgreining, r.utbyting,
                    r.skjalategund, tm.nefnd, tm.html, r.flutningsmadur_name, r.flutningsmadur_radherra, tm.thingflokkur
                    FROM RankedFlutningsmadur r
                    JOIN thingmal tm ON r.malsnumer = tm.malnumer
                    JOIN malaskra m ON r.malsnumer = m.malsnumer
                    LEFT JOIN thingmenn tm ON r.flutningsmadur_name = tm.nafn
                    WHERE r.skjalategund IN ('frumvarp', 'þáltill.', 'stjórnarfrumvarp', 'stjórnartillaga', 'frumvarp nefndar')
                    AND r.row_num = 1;""",
        "template_file": 'thingmal_template.html',
        "output_file": 'thingmal.html',
        "context": {'filter': 'none'}
    },
    {
        "query": """SELECT t1.id, t1.skjalsnumer, fm.nafn, t1.malsnumer, tm.html, tm.malsheiti,
                        tm.stadamals, t1.utbyting, t1.skjalategund,
                        CASE WHEN t1.skjalategund = 'svar' THEN t2.utbyting ELSE strftime('%Y-%m-%d', 'now') END AS svar_dagsetning,
                        CASE WHEN t1.skjalategund = 'svar' THEN (julianday(t2.utbyting) - julianday(t1.utbyting)) * 5 / 7
                        ELSE (julianday(strftime('%Y-%m-%d', 'now')) - julianday(t1.utbyting)) * 5 / 7 END AS days_between
                    FROM thingskjal t1
                    LEFT JOIN thingskjal t2 ON t1.malsnumer = t2.malsnumer AND t2.skjalategund = 'svar'
                    JOIN thingmal tm ON t1.malsnumer = tm.malnumer
                    JOIN flutningsmadur fm ON t1.skjalsnumer = fm.skjalsnumer
                    WHERE t1.skjalategund = 'fsp. til skrifl. svars';""",
        "template_file": 'fyrirspurnir_template.html',
        "output_file": 'fyrirspurnir.html',
        "context": {'filter': 'none'}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_tegund = "ft";""",
        "template_file": 'oundirbunar_template.html',
        "output_file": 'raedur_oundirbunar.html',
        "context": {}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_tegund = "st";""",
        "template_file": 'storfin_template.html',
        "output_file": 'raedur_storfin.html',
        "context": {}
    },
    {
        "query": """SELECT r.*, tm.* FROM raedur r
                    JOIN thingmenn tm ON r.raedumadur = tm.nafn
                    WHERE mal_heiti NOT NULL AND raeda_texti != ""
                    ORDER BY id DESC;""",
        "template_file": 'raedur_timarod_template.html',
        "output_file": 'raedur_timarod.html',
        "context": {}
    }
]

# Placeholder labels for þjóðhagsspá data
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