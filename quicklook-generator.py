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

def main():
    md_file = 'bold-technical-deep-dive.md'
    json_file = 'glossary.json'

    md_content = parse_md_file(md_file)
    json_data = load_json_file(json_file)

    md_content_with_quicklook = replace_with_quicklook(md_content, json_data)

    # Write the modified Markdown content to a new file
    with open('md_content_with_quicklook.md', 'w') as f:
        f.write(md_content_with_quicklook)

if __name__ == "__main__":
    main()
