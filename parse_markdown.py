import re
import json
from typing import Dict, List, Optional

def parse_markdown_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into individual entries
    entries = content.split('---')
    parsed_entries = []

    for entry in entries:
        if not entry.strip():
            continue
        
        parsed_entry = parse_single_entry(entry.strip())
        if parsed_entry:
            parsed_entries.append(parsed_entry)

    return parsed_entries

def parse_single_entry(entry: str) -> Optional[Dict]:
    entry_data = {}
    
    # Extract title
    title_match = re.search(r'###\s*\d+\.\s*\*\*(.*?)\*\*', entry)
    if not title_match:  # Skip entries without a title
        return None
    
    entry_data['title'] = title_match.group(1).strip()
    
    # Extract basic fields
    fields = {
        'Date': r'\*\*Date\*\*:\s*(.*?)(?:\n|$)',
        'Group': r'\*\*Group\*\*:\s*(.*?)(?:\n|$)',
        'Inventor': r'\*\*Inventor\*\*:\s*(.*?)(?:\n|$)',
        'Don Ihde Categories': r'\*\*Don Ihde Categories\*\*:\s*(.*?)(?:\n|$)'
    }
    
    for field, pattern in fields.items():
        match = re.search(pattern, entry)
        if match:
            entry_data[field.lower().replace(' ', '_')] = match.group(1).strip()

    # Extract diagrams
    diagrams = []
    diagram_blocks = re.finditer(
        r'\s*-\s*\*\*Type\*\*:\s*\*?\*?(.*?)\*?\*?\n'
        r'(?:\s*-?\s*\*\*Base Diagram\*\*:\s*`?(.*?)`?\n)?'
        r'(?:\s*-?\s*\*\*Olog Diagram\*\*:\s*```(?:\n)?(.*?)```\n)?'
        r'(?:\s*-?\s*\*\*Situation\*\*:\s*(.*?)(?=\n\s*-\s*\*\*Type|\n\s*---|$))?',
        entry,
        re.DOTALL
    )

    for diagram in diagram_blocks:
        diagram_data = {
            'type': diagram.group(1).strip().replace('*', ''),
            'base_diagram': diagram.group(2).strip() if diagram.group(2) else None,
            'olog_diagram': diagram.group(3).strip() if diagram.group(3) else None,
            'situation': diagram.group(4).strip() if diagram.group(4) else None
        }
        # Clean up any remaining markdown artifacts
        for key, value in diagram_data.items():
            if value:
                diagram_data[key] = value.replace('*', '')
        diagrams.append(diagram_data)

    if diagrams:
        entry_data['diagrams'] = diagrams

    return entry_data

def main():
    input_file = 'data.md'
    output_file = 'parsed_data.json'
    
    try:
        entries = parse_markdown_file(input_file)
        
        # Write to JSON file with proper formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully parsed {len(entries)} entries to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
