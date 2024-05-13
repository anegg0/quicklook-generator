# README

## Quicklook Generator

### Project description

Quicklook Generator is a CLI utility that helps you populate a markdown file with `quicklook` tags, while attending a call or arguing over Slack.

### Who this project is for

This project is intended for OCL TWs; otherwise, you'd be hard-pressed to find any value in this thing (and it doesn't have much, anyway).
Also, if you are a malicious actor, be aware that this utility will give you access to some OSS code on github, so have fun accomplishing nothing!

### Prerequisites

Before using Quicklook Generator, ensure you have:
* MacOS 12+
* Some familiarity with `CLI`

### Install 

``` sh
bash <(wget -qO- https://github.com/anegg0/quicklook-generator/blob/main/install-script-quicklook-generator.sh)
```
Or, if you don't want to see what the install script is going to do to your system, feel free to pick a binary in the releases. Add it to your $PATH, and it'll work on your machine, too.

### Usage 

1. Run:

``` sh
quicklook-generator <your-input-file>.md  <your-output-file>.md
```
- The generator will output a fascinating `<your-output-file>.md` with some `quicklook` tags elegantly spread on it (**if** it could find a match between your text and the [glossary](https://raw.githubusercontent.com/OffchainLabs/arbitrum-docs/master/website/static/glossary.json)). 
- To avoid noise generation, the script will only add one `quicklook` per match.

2. Diff the output file with your favorite editor to remove the `quicklooks` you consider unnecessary.


### Terms of use
Quicklook Generator is licensed under MIT.

