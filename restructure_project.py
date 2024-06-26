import os
import shutil

# Define the new structure
new_structure = {
    'src': [
        'fetch_xml.py', 'process_thingskjol.py', 'generate_html.py', 'main.py', 
        'database_setup.py', 'get_data.py', 'get_hagstofa.py', 'issue_status.py', 
        'postur.py', 'query.py', 'create_html.py'
    ],
    'data': [],  # Assuming all data files are already in a folder named 'data'
    'templates': [],  # Directory for HTML template files
    'db': ['thing.db'],  # Add your database files here
    'output': [],  # Directory for HTML output files
    'root': ['README.md', 'requirements.txt']
}

# Create directories
def create_directories(base_path, directories):
    for directory in directories:
        path = os.path.join(base_path, directory)
        if not os.path.exists(path):
            os.makedirs(path)

# Move files to their new locations
def move_files(base_path, structure):
    for folder, files in structure.items():
        for file in files:
            src_path = os.path.join(base_path, file)
            if os.path.exists(src_path):
                dest_path = os.path.join(base_path, folder, file)
                shutil.move(src_path, dest_path)
                print(f"Moved {file} to {folder}/")

# Move template HTML files to the templates directory
def move_template_html_files(base_path):
    for file_name in os.listdir(base_path):
        if file_name.endswith('.html') and 'template' in file_name:
            src_path = os.path.join(base_path, file_name)
            dest_path = os.path.join(base_path, 'templates', file_name)
            shutil.move(src_path, dest_path)
            print(f"Moved template {file_name} to templates/")

# Move output HTML files to the output directory
def move_output_html_files(base_path):
    for file_name in os.listdir(base_path):
        if file_name.endswith('.html') and 'template' not in file_name:
            src_path = os.path.join(base_path, file_name)
            dest_path = os.path.join(base_path, 'output', file_name)
            shutil.move(src_path, dest_path)
            print(f"Moved output {file_name} to output/")

# Main function to restructure the project
def restructure_project(base_path):
    create_directories(base_path, new_structure.keys())
    move_files(base_path, new_structure)
    move_template_html_files(base_path)
    move_output_html_files(base_path)

if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))  # Set the base path to the current directory
    restructure_project(base_path)
    print("Project restructuring complete.")
