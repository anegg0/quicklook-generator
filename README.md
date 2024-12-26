# README

## Quicklook Generator

### Project description

Quicklook Generator is a CLI utility that helps you populate a markdown file with `quicklook` tags while arguing over Slack.

### Who this project is for

This project is intended for OCL TWs; otherwise, you'd be hard-pressed to find any value in this thing (and it doesn't have much, anyway).

### Prerequisites

Before using Quicklook Generator, ensure you have the following:
* MacOS 12+
* Some familiarity with `CLI`

### Install 
#### Using the install script
``` sh
bash <(wget -O- https://raw.githubusercontent.com/anegg0/quicklook-generator/main/install-script-quicklook-generator.sh)
```
#### Manual installation

Pick a binary from the releases. Add it to your $PATH, and it'll work on your machine, too.

### Usage 

1. Run:

``` sh
quicklook_generator <your-input-file>.md  <your-output-file>.md
```
- The generator will output a fascinating `<your-output-file>.md` with some `quicklook` tags elegantly spread on it (**if** it could find a match between your text and the [glossary](https://raw.githubusercontent.com/OffchainLabs/arbitrum-docs/master/website/static/glossary.json)). 
- The script will only add one `quicklook` per match to avoid noise generation.

2. Diff the output file with your favorite editor to remove the `quicklooks` you consider unnecessary.

### Devs
You know what to do if you ever want to do something with this.

### Terms of use
Quicklook Generator is licensed under GPL-3.0.

