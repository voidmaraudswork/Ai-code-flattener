import os
import zipfile
import shutil
import sys
from pathlib import Path

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build'}
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.html', '.css', '.c', '.cpp', '.java', '.go', '.rs', '.php', '.md', '.txt', '.json', '.yaml', '.yml'}

def preprocess_zip(zip_path, output_filename="processed_code.md"):
    extract_dir = "temp_extracted_repo"
    
    if not os.path.exists(zip_path):
        print(f"Error: File {zip_path} not found")
        return

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Repository Context: {os.path.basename(zip_path)}\n\n")
        
        for root, dirs, files in os.walk(extract_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    relative_path = file_path.relative_to(extract_dir)
                    outfile.write(f"## FILE: {relative_path}\n")
                    outfile.write(f"```{file_path.suffix[1:]}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            outfile.write(f.read())
                    except:
                        outfile.write("[Error reading file]")
                    outfile.write("\n```\n\n")

    shutil.rmtree(extract_dir)
    print(f"Successfully created {output_filename}")

if __name__ == "__main__":
    # This takes the filename from the GitHub Action command
    if len(sys.argv) > 1:
        zip_input = sys.argv[1]
        preprocess_zip(zip_input)
    else:
        print("No zip file provided.")
