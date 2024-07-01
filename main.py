<<<<<<< HEAD
import subprocess

def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")

if __name__ == '__main__':
    # Run the data fetching script
    run_script('src/fetch_all_data.py')

    # Run the setup HTML script
    run_script('src/setup_html.py')

    # Run the generate HTML script
    run_script('src/generate_html.py')

    print("All scripts executed successfully.")
=======
import os
import subprocess
import sqlite3
import sys
from scripts.utils import cache_or_fetch

def reset_db():
    conn = sqlite3.connect('thing.db')
    cursor = conn.cursor()
    tables = ['thingmenn', 'malaskra', 'thingskjol', 'dagskra', 'raedur']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    conn.commit()
    conn.close()

def main():
    force = 'true' if '--force' in sys.argv else 'false'

    # Fetch information about the current session
    url = "https://www.althingi.is/altext/xml/loggjafarthing/yfirstandandi/"
    data = cache_or_fetch(url, force)

    # Extract information from the parsed data
    yfirstandandi = data['löggjafarþing']['þing']

    try:
        current_session = yfirstandandi[u'@númer']
    except:
        print(u'Tókst ekki að ná í núverandi þing, reyndu aftur síðar. Mögulega er xml þjónusta þingsins niðri')
        sys.exit(0)    

    print("Næ í upplýsingar um löggjafarþing: ", current_session)

    # Reset the database
    reset_db()

    # Run each fetch script
    scripts = [
        'fetch_thingmenn.py',
        'fetch_malaskra.py',
        'fetch_thingskjol.py',
        'fetch_dagskra.py',
        'fetch_raedur.py'
    ]

    for script in scripts:
        print(f"Running {script}...")
        subprocess.run(['python', os.path.join('scripts', script), force, current_session])

if __name__ == '__main__':
    main()
>>>>>>> new
