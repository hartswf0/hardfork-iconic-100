#!/usr/bin/env python3

import re
import json
from typing import Optional, Dict, List

def clean_text(text: str) -> str:
    """Clean text by removing markdown artifacts and extra whitespace."""
    return text.replace('*', '').strip()

def extract_code_block(text: str) -> Optional[str]:
    """Extract and clean a code block while preserving its structure."""
    lines = text.splitlines()
    
    # Remove empty lines from start and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
        
    if not lines:
        return None
        
    # Find minimum indentation from non-empty lines
    min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    
    # Remove that amount of indentation from all lines
    cleaned_lines = [line[min_indent:] if line.strip() else '' for line in lines]
    
    # Return with code block markers
    return '```\n' + '\n'.join(cleaned_lines) + '\n```'

def parse_diagram_section(section: str) -> Optional[Dict]:
    """Parse a single diagram section."""
    # Extract type
    type_match = re.match(r'\s*\*?\*?(.*?)\*?\*?\n', section)
    if not type_match:
        return None
        
    diagram_data = {
        'type': clean_text(type_match.group(1)),
        'base_diagram': None,
        'olog_diagram': None,
        'situation': None
    }
    
    # Extract base diagram
    base_match = re.search(r'\*\*Base Diagram\*\*:\s*`?(.*?)`?\n', section)
    if base_match:
        diagram_data['base_diagram'] = clean_text(base_match.group(1))
    
    # Extract Olog diagram - handle both indented and non-indented cases
    olog_match = re.search(
        r'\*\*Olog Diagram\*\*:\s*\n\s*```\n(.*?)\n\s*```',
        section,
        re.DOTALL
    )
    if olog_match:
        olog_content = olog_match.group(1)
        diagram_data['olog_diagram'] = extract_code_block(olog_content)
    
    # Extract situation - handle both single and multi-line cases
    situation_match = re.search(
        r'\*\*Situation\*\*:\s*(.*?)(?=\n\s*(?:-\s*\*\*Type|\s*---)|\s*$)',
        section,
        re.DOTALL
    )
    if situation_match:
        situation = situation_match.group(1).strip()
        if situation:
            diagram_data['situation'] = clean_text(situation)
    
    return diagram_data

def parse_entry(entry: str) -> Optional[Dict]:
    """Parse a single markdown entry."""
    try:
        # Extract title - handle both numbered and unnumbered entries
        title_match = re.search(r'###\s*(?:\d+\.)?\s*\*\*(.*?)\*\*', entry)
        if not title_match:
            return None
            
        entry_data = {'title': clean_text(title_match.group(1))}
        
        # Extract basic fields
        fields = {
            'date': r'\*\*Date\*\*:\s*(.*?)(?:\n|$)',
            'group': r'\*\*Group\*\*:\s*(.*?)(?:\n|$)',
            'inventor': r'\*\*Inventor\*\*:\s*(.*?)(?:\n|$)',
            'don_ihde_categories': r'\*\*Don Ihde Categories\*\*:\s*(.*?)(?:\n|$)'
        }
        
        for field, pattern in fields.items():
            match = re.search(pattern, entry)
            if match:
                entry_data[field] = clean_text(match.group(1))
        
        # Split into diagram sections and parse each
        diagrams = []
        diagram_sections = re.split(r'\n\s*-\s*\*\*Type\*\*:', entry)[1:]
        
        for section in diagram_sections:
            diagram_data = parse_diagram_section(section)
            if diagram_data:
                diagrams.append(diagram_data)
        
        if diagrams:
            entry_data['diagrams'] = diagrams
            
        return entry_data
        
    except Exception as e:
        print(f"Error parsing entry starting with: {entry[:100]}...")
        print(f"Error details: {str(e)}")
        return None

def main():
    try:
        # Read markdown file
        with open('data.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into entries
        entries = re.split(r'\n\s*---\s*\n', content)
        
        # Parse each entry
        parsed_entries = []
        for entry in entries:
            if entry.strip():
                parsed_entry = parse_entry(entry)
                if parsed_entry:
                    parsed_entries.append(parsed_entry)
        
        # Write to JSON file
        with open('upstream_running.json', 'w', encoding='utf-8') as f:
            json.dump(parsed_entries, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully parsed {len(parsed_entries)} entries to upstream_running.json")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == '__main__':
    main()
