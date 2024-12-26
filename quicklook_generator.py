import argparse
import re
import json
import requests  # Import the requests library

# Hardcode the URL for the JSON glossary
GLOSSARY_URL = 'https://raw.githubusercontent.com/OffchainLabs/arbitrum-docs/master/website/static/glossary.json'

def parse_md_file(md_file):
    with open(md_file, 'r') as f:
        md_content = f.read()
    return md_content

def load_json_from_url():
    # Use requests to fetch the JSON data from the hardcoded URL
    response = requests.get(GLOSSARY_URL)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()  # Returns the JSON content

def replace_with_quicklook(md_content, pairs):
    lines = md_content.splitlines()
    inside_code_block = False
    inside_skippable_section = False
    replaced_terms = set()  # Track which terms have been replaced

    # Create a mapping of lowercase terms to their preferred display case
    term_cases = {search_term.lower(): replace_term.split('>')[1].split('<')[0] 
                  for search_term, replace_term in pairs}
    
    # Create a mapping of lowercase terms to their preferred tag type
    tag_types = {search_term.lower(): search_term.lower().replace(' ', '-')
                 for search_term, _ in pairs}

    # Regex patterns
    md_link_pattern = r'\[([^\]]+)\]\([^)]+\)'  # [text](url)
    html_link_pattern = r'<a[^>]*>.*?</a>'      # <a>text</a>
    inline_code_pattern = r'`[^`]*`'            # `code` (non-greedy match)
    variable_pattern = r'@[^@]+@'               # @variable@ pattern
    existing_quicklook = r'<a\s+data-quicklook-from="([^"]+)"[^>]*>([^<]+)</a>'  # Existing quicklook tags

    # First pass: remove existing quicklook tags but preserve their text content
    cleaned_lines = []
    for line in lines:
        # Extract and store the original text from quicklook tags
        while True:
            match = re.search(existing_quicklook, line)
            if not match:
                break
            # Replace the entire tag with just the text content
            _, text = match.groups()
            line = line[:match.start()] + text + line[match.end():]
        cleaned_lines.append(line)

    # Now process the cleaned lines
    for i, line in enumerate(cleaned_lines):
        # Toggle the code block flag
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block
            continue

        # Skip code blocks and headers
        if inside_code_block or line.startswith("#"):
            continue

        # Toggle the skippable section flag
        if line.strip() == "---":
            inside_skippable_section = not inside_skippable_section
            continue

        if inside_skippable_section:
            continue

        # Find all protected regions and their contents
        protected_regions = []
            
        # Find inline code regions (including backticks)
        for match in re.finditer(inline_code_pattern, line):
            start, end = match.span()
            # Include the backticks in the protected region
            protected_regions.append((start, end))
            # Also protect one character before and after if they exist
            if start > 0:
                protected_regions.append((start - 1, start))
            if end < len(line):
                protected_regions.append((end, end + 1))
            
        # Find variable regions
        for match in re.finditer(variable_pattern, line):
            protected_regions.append((match.start(), match.end()))
            
        # Find markdown links and their text
        for match in re.finditer(md_link_pattern, line):
            # Protect the entire link region
            protected_regions.append((match.start(), match.end()))
            # Also protect one character before and after if they exist
            if match.start() > 0:
                protected_regions.append((match.start() - 1, match.start()))
            if match.end() < len(line):
                protected_regions.append((match.end(), match.end() + 1))
            
        # Find HTML links (excluding quicklook tags which we've already removed)
        for match in re.finditer(html_link_pattern, line):
            protected_regions.append((match.start(), match.end()))
            # Also protect one character before and after if they exist
            if match.start() > 0:
                protected_regions.append((match.start() - 1, match.start()))
            if match.end() < len(line):
                protected_regions.append((match.end(), match.end() + 1))

        # Sort and merge overlapping regions
        if protected_regions:
            protected_regions.sort()
            merged_regions = [protected_regions[0]]
            for current in protected_regions[1:]:
                previous = merged_regions[-1]
                if current[0] <= previous[1] + 1:  # Allow 1 character gap
                    merged_regions[-1] = (previous[0], max(previous[1], current[1]))
                else:
                    merged_regions.append(current)
            protected_regions = merged_regions

        # Process each term
        for search_term, _ in pairs:
            # Skip if term has already been replaced somewhere in the document
            term_lower = search_term.lower()
            if term_lower in replaced_terms:
                continue
                
            # Case insensitive search pattern with word boundaries
            search_pattern = re.escape(search_term)
            
            # Find all potential term matches
            for match in re.finditer(rf'\b{search_pattern}\b', line, flags=re.IGNORECASE):
                term_start, term_end = match.span()
                
                # Check if the term is inside or adjacent to any protected region
                is_protected = False
                for region_start, region_end in protected_regions:
                    # Check if term overlaps with or is adjacent to a protected region
                    if (term_start >= region_start and term_start <= region_end) or \
                       (term_end >= region_start and term_end <= region_end):
                        is_protected = True
                        break
                
                # If term is not protected, replace it
                if not is_protected:
                    # Use the preferred case for the term
                    term_text = term_cases.get(term_lower, match.group(0))
                    tag_type = tag_types[term_lower]
                    replacement = f'<a data-quicklook-from="{tag_type}">{term_text}</a>'
                    line = line[:term_start] + replacement + line[term_end:]
                    replaced_terms.add(term_lower)
                    break  # Only replace first occurrence of term

        cleaned_lines[i] = line

    return "\n".join(cleaned_lines)

def main(args):
    md_file = args.input_md

    md_content = parse_md_file(md_file)
    json_data = load_json_from_url()  # Fetch JSON from the hardcoded URL

    pairs = [(value['title'], f'<a data-quicklook-from="{key}">{value["title"]}</a>') for key, value in json_data.items()]

    md_content_with_quicklook = replace_with_quicklook(md_content, pairs)

    # Write the modified Markdown content to the output file
    with open(args.output_md, 'w') as f:
        f.write(md_content_with_quicklook)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Replace terms in Markdown file with quicklook tags.')
    parser.add_argument('input_md', help='Input Markdown file')
    parser.add_argument('output_md', help='Output Markdown file')
    args = parser.parse_args()
    main(args)
