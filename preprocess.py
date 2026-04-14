import os
import zipfile
import shutil
from pathlib import Path

# Configuration: Folders and files to ignore
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.idea', '.vscode'}
IGNORE_FILES = {'.DS_Store', 'package-lock.json', 'yarn.lock'}
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.html', '.css', '.c', '.cpp', '.java', '.go', '.rs', '.php', '.md', '.txt', '.json', '.yaml', '.yml'}

def is_text_file(file_path):
    """Check if a file is likely a text file by reading a small chunk."""
    try:
        with open(file_path, 'tr', encoding='utf-8') as f:
            f.read(1024)
            return True
    except (UnicodeDecodeError, PermissionError):
        return False

def preprocess_zip(zip_path, output_filename="processed_code.md"):
    extract_dir = "temp_extracted_repo"
    
    # 1. Extract the ZIP
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # 2. Iterate and concatenate
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Repository Context: {os.path.basename(zip_path)}\n\n")
        
        # Walk through the directory
        for root, dirs, files in os.walk(extract_dir):
            # Modify dirs in-place to skip ignored folders
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                # Filter: Only include text-based source files
                if ext in ALLOWED_EXTENSIONS or is_text_file(file_path):
                    relative_path = file_path.relative_to(extract_dir)
                    
                    print(f"Adding: {relative_path}")
                    
                    # Add a header for the file
                    outfile.write(f"## FILE: {relative_path}\n")
                    outfile.write(f"```{ext.replace('.', '') if ext else 'text'}\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            outfile.write(f.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    
                    outfile.write("\n```\n\n")

    # 3. Cleanup
    shutil.rmtree(extract_dir)
    print(f"\nDone! All code merged into: {output_filename}")

if __name__ == "__main__":
    zip_input = input("Enter the path to the ZIP file: ").strip().strip('"')
    if os.path.exists(zip_input):
        preprocess_zip(zip_input)
    else:
        print("File not found.")
