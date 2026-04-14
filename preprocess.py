import streamlit as st
import zipfile
import os
import shutil
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Code Preprocessor", page_icon="📁")

# Folders to skip
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.idea', '.vscode'}
# Files to skip
IGNORE_FILES = {'.DS_Store', 'package-lock.json', 'yarn.lock'}
# Extensions to include
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.html', '.css', '.c', '.cpp', '.java', '.go', '.rs', '.php', '.md', '.txt', '.json', '.yaml', '.yml', '.sql'}

def is_text_file(file_path):
    try:
        with open(file_path, 'tr', encoding='utf-8') as f:
            f.read(1024)
            return True
    except:
        return False

# --- UI ---
st.title("📂 AI Code Preprocessor")
st.write("Upload a ZIP file of your project to convert it into a single Markdown file for AI context.")

uploaded_zip = st.file_uploader("Choose a ZIP file", type="zip")

if uploaded_zip:
    extract_dir = "temp_extraction"
    output_filename = "processed_code.md"
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with st.spinner("Processing files..."):
        # 1. Extract ZIP
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # 2. Build the flattened content
        flattened_content = f"# Repository: {uploaded_zip.name}\n\n"
        
        file_count = 0
        for root, dirs, files in os.walk(extract_dir):
            # Ignore hidden/junk folders
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
            
            for file in files:
                if file in IGNORE_FILES or file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                if ext in ALLOWED_EXTENSIONS or is_text_file(file_path):
                    relative_path = file_path.relative_to(extract_dir)
                    
                    flattened_content += f"## FILE: {relative_path}\n"
                    # Determine code block language
                    lang = ext.replace('.', '') if ext else 'text'
                    flattened_content += f"```{lang}\n"
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            flattened_content += f.read()
                    except Exception as e:
                        flattened_content += f"[Error reading file: {e}]"
                    
                    flattened_content += "\n```\n\n"
                    file_count += 1

        # 3. Success UI
        st.success(f"Done! Processed {file_count} files.")
        
        # 4. Download Button
        st.download_button(
            label="📥 Download Flattened Code (.md)",
            data=flattened_content,
            file_name="processed_code.md",
            mime="text/markdown"
        )

        # Show a preview
        with st.expander("Preview Output"):
            st.code(flattened_content[:2000] + "...", language="markdown")

    # Cleanup
    shutil.rmtree(extract_dir)
