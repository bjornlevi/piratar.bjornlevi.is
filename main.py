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
