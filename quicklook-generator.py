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
    replaced_terms = set()

    for i, line in enumerate(lines):
        # Toggle the code block flag
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block

        if inside_code_block or line.startswith("#") or "**" in line:
            continue

        # Toggle the skippable section flag
        if line.strip() == "---":
            inside_skippable_section = not inside_skippable_section
            continue

        if inside_skippable_section:
            continue

        for search_term, replace_term in pairs:
            if search_term in replaced_terms:
                continue

            search_pattern = re.escape(search_term)
            line, num_replacements = re.subn(rf'\b{search_pattern}\b',
                                             replace_term,
                                             line,
                                             count=1)

            if num_replacements > 0:
                replaced_terms.add(search_term)
                break  # Exit the loop after first replacement to prevent multiple replacements in the same line

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
