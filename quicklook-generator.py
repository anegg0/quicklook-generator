import argparse
import markdown
import re
import json

def parse_md_file(md_file):
    with open(md_file, 'r') as f:
        md_content = f.read()
    return md_content

def load_json_file(json_file):
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    return json_data

def replace_with_quicklook(md_content, json_data):
    for key, value in json_data.items():
        title = value['title']
        md_content = re.sub(r'\b{}\b'.format(title), f'<a data-quicklook-from="{key}">{title}</a>', md_content)
    return md_content

def main(args):
    md_file = args.input_md
    json_file = args.glossary

    md_content = parse_md_file(md_file)
    json_data = load_json_file(json_file)

    md_content_with_quicklook = replace_with_quicklook(md_content, json_data)

    # Write the modified Markdown content to the output file
    with open(args.output_md, 'w') as f:
        f.write(md_content_with_quicklook)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Replace terms in Markdown file with quicklook tags.')
    parser.add_argument('input_md', help='Input Markdown file')
    parser.add_argument('output_md', help='Output Markdown file')
    parser.add_argument('glossary', help='JSON glossary file')
    args = parser.parse_args()
    main(args)
