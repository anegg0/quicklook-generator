# Quicklook Generator

A tool to automatically add quicklook tags to your Markdown documentation.

## Installation

### Prerequisites
- macOS
- `wget` (can be installed via `brew install wget`)

### Quick Install
```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/anegg0/quicklook-generator/main/install-script-quicklook-generator.sh | bash
```

### Manual Installation
1. Download the latest release from the [releases page](https://github.com/anegg0/quicklook-generator/releases)
2. Make it executable: `chmod +x quicklook_generator`
3. Move it to a directory in your PATH: `mv quicklook_generator ~/.local/bin/`

## Usage

```bash
quicklook_generator input.md output.md
```

This will:
1. Read your input Markdown file
2. Fetch the latest glossary terms
3. Add quicklook tags to matching terms
4. Save the result to your output file

## Example

Input (`input.md`):
```markdown
This document discusses Arbitrum One and its features.
```

Output (`output.md`):
```markdown
This document discusses <a data-quicklook-from="arbitrum-one">Arbitrum One</a> and its features.
```

## Building from Source

If you prefer to build from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/anegg0/quicklook-generator.git
   cd quicklook-generator
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the script:
   ```bash
   python quicklook_generator.py input.md output.md
   ```

## License

[MIT License](LICENSE)

