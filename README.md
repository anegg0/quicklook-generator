# README

## Quicklook Generator

### Project description

Quicklook Generator helps you populate a markdown file with `quicklooks` tags while attending a call or arguing over Slack.


### Who this project is for

This project is intended EXCLUSIVELY for OCL TW; otherwise, you'd be hard-pressed to find any benefit in this utility.
Also, if you are a malicious actor, be aware that this utility has been thoroughly edited to give you access to some OSS code.


### Prerequisites

Before using {Project Name}, ensure you have:
* MacOS 12+ 
* Being used to `CLI`
* Being so darn lazy you can't even copy-paste those poor `quicklooks` without feeling triggered

### Install 

``` sh
bash <(wget -qO- https://github.com/anegg0/quicklook-generator/blob/main/install-script-quicklook-generator.sh)
```

### Usage 

1. Run:

``` sh
quicklook-generator <your-input-file>.md  <your-output-file>.md
```

The generator will output a gorgeous `<your-output-file>.md` with some `quicklooks` tags elegantly spread in it (if it could find a match between your text and the [glossary](https://raw.githubusercontent.com/OffchainLabs/arbitrum-docs/master/website/static/glossary.json)). 
To avoid noise generation, the script will only add one `quicklook` per match.

2. Diff the output file with your favorite editor to remove the `quicklooks` you consider unnecessary.


### Terms of use
Quicklook Generator is licensed under MIT.

