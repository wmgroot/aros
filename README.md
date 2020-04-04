# aros
A helper tool to generate content from https://www.kickstarter.com/projects/dastardlydave/a-rasp-of-sand-a-roguelike-tabletop-rpg-experience

## Installation

* Important: this tool does not function without an accompanying configuration file that contains the Rasp of Sand content.

First ensure you have Python 3.5+ installed.
```
python --version
Python 3.7.6
```

Clone the source code.
```
cd ~
git clone git@github.com:wmgroot/aros.git
```

Install the command line interface locally.
```
$ pip install -e ~/aros
Obtaining file:///Users/mgroot/aros
Requirement already satisfied: ruamel.yaml==0.15.100 in /usr/local/lib/python3.7/site-packages (from aros==0.0.1) (0.15.100)
Installing collected packages: aros
  Found existing installation: aros 0.0.1
    Uninstalling aros-0.0.1:
      Successfully uninstalled aros-0.0.1
  Running setup.py develop for aros
Successfully installed aros
```

## Use
Run the tool on the command line.
```
aros map pelagic -s awesome_seed
Seed: awesome_seed
```
[Imgur](https://i.imgur.com/u2BgBhV.png)
