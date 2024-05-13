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
    # Split the content into lines to process each individually
    lines = md_content.splitlines()
    inside_skippable_section = False
    replaced_terms = set()  # Set to keep track of terms that have already been replaced

    for i, line in enumerate(lines):
        # Check if the line marks the start or end of a skippable section
        if line.strip() == "---":
            inside_skippable_section = not inside_skippable_section
            continue

        # Skip processing lines within skippable sections or if it's a title or contains bold text
        if inside_skippable_section or line.startswith("#") or "**" in line:
            continue

        for search_term, replace_term in pairs:
            # Skip this term if it has already been replaced once
            if search_term in replaced_terms:
                continue

            search_pattern = re.escape(search_term)

            # Perform a single substitution with re.subn()
            line, num_replacements = re.subn(rf'\b{search_pattern}\b',
                                             replace_term,
                                             line,
                                             count=1)  # Limit to one replacement

            # If a replacement was made, add the term to the replaced_terms set
            if num_replacements > 0:
                replaced_terms.add(search_term)

        lines[i] = line

    # Join the lines back into the full content
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
