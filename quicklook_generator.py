import argparse
import markdown
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

    # Regex patterns for links
    md_link_pattern = r'\[([^\]]+)\]\([^)]+\)'  # [text](url)
    html_link_pattern = r'<a[^>]*>.*?</a>'      # <a>text</a>

    for i, line in enumerate(lines):
        # Toggle the code block flag
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block

        # Skip code blocks and headers
        if inside_code_block or line.startswith("#"):
            continue

        # Toggle the skippable section flag
        if line.strip() == "---":
            inside_skippable_section = not inside_skippable_section
            continue

        if inside_skippable_section:
            continue

        # Find all links in the line
        all_links = []
        for match in re.finditer(md_link_pattern, line):
            all_links.append((match.start(), match.end()))
        for match in re.finditer(html_link_pattern, line):
            all_links.append((match.start(), match.end()))

        # Process each term
        for search_term, replace_term in pairs:
            # Skip if term has already been replaced somewhere in the document
            if search_term in replaced_terms:
                continue
                
            # Case insensitive search pattern with word boundaries
            search_pattern = re.escape(search_term)
            
            # Find all potential term matches
            for match in re.finditer(rf'\b{search_pattern}\b', line, flags=re.IGNORECASE):
                term_start, term_end = match.span()
                
                # Check if the term is part of or adjacent to any link
                is_near_link = False
                for link_start, link_end in all_links:
                    # Check if term overlaps with or is adjacent to a link
                    if (term_start >= link_start - 1 and term_start <= link_end + 1) or \
                       (term_end >= link_start - 1 and term_end <= link_end + 1):
                        is_near_link = True
                        break
                
                # If term is not near any link, replace it
                if not is_near_link:
                    line = line[:term_start] + replace_term + line[term_end:]
                    replaced_terms.add(search_term)
                    break  # Only replace first occurrence of term

        lines[i] = line

    return "\n".join(lines)

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
