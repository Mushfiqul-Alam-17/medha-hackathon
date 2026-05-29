import os
import re
from pathlib import Path

def extract_files(guide_path, output_dir):
    with open(guide_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file = None
    file_content = []
    
    # Modes: 'mcp' for ===FILE blocks, 'editor' for file_editor create blocks
    mode = None 

    for i, line in enumerate(lines):
        # Match the start of an MCP file block
        match_mcp = re.search(r'===FILE:\s*(.+)$', line.strip())
        if match_mcp and mode is None:
            current_file = match_mcp.group(1).strip()
            mode = 'mcp'
            if current_file.startswith('/app/'):
                current_file = current_file[5:]
            elif current_file.startswith('/'):
                current_file = current_file[1:]
            
            file_content = []
            continue
        
        # Match the end of an MCP file block
        if line.strip() == '===END' and mode == 'mcp':
            out_path = Path(output_dir) / current_file
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            start_idx = 0
            if len(file_content) > 0 and file_content[0].strip().endswith(current_file + ':'):
                start_idx = 1
            elif len(file_content) > 0 and file_content[0].strip() == current_file + ':':
                start_idx = 1
                
            with open(out_path, 'w', encoding='utf-8') as out_f:
                for content_line in file_content[start_idx:]:
                    content_line = re.sub(r'^\d+\|', '', content_line)
                    out_f.write(content_line)
            
            print(f'Extracted MCP: {out_path}')
            current_file = None
            file_content = []
            mode = None
            continue
            
        # Match the start of a file_editor create block
        match_editor = re.match(r'^Action: file_editor create\s+([^\s]+)\s+--file-text\s+"(.*)$', line)
        if match_editor and mode is None:
            current_file = match_editor.group(1).strip()
            mode = 'editor'
            if current_file.startswith('/app/'):
                current_file = current_file[5:]
            elif current_file.startswith('/'):
                current_file = current_file[1:]
            
            file_content = []
            if match_editor.group(2):
                file_content.append(match_editor.group(2) + '\n')
            continue

        # Match the end of a file_editor create block
        if mode == 'editor':
            # It ends with a single double quote " on a line, followed by Observation: Overwrite successful
            if line.strip() == '"' and i+1 < len(lines) and 'Observation:' in lines[i+1]:
                out_path = Path(output_dir) / current_file
                out_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    for content_line in file_content:
                        # For editor blocks, no line numbers to strip, just raw content
                        out_f.write(content_line)
                
                print(f'Extracted Editor: {out_path}')
                current_file = None
                file_content = []
                mode = None
                continue
            elif re.search(r'"$', line.rstrip('\n')) and i+1 < len(lines) and 'Observation:' in lines[i+1]:
                # In case the quote is at the end of the last line of code
                file_content.append(re.sub(r'"$', '', line))
                out_path = Path(output_dir) / current_file
                out_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    for content_line in file_content:
                        out_f.write(content_line)
                
                print(f'Extracted Editor: {out_path}')
                current_file = None
                file_content = []
                mode = None
                continue
            else:
                file_content.append(line)
        
        if mode == 'mcp':
            file_content.append(line)
            
if __name__ == "__main__":
    guide_path = r"c:\Users\mushf\Downloads\Medha\guide"
    output_dir = r"c:\Users\mushf\Downloads\Medha\app"
    extract_files(guide_path, output_dir)
