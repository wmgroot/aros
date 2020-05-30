# aros
A helper tool to automatically generate content for A Rasp of Sand, a tabletop RPG Zine.

## Thanks
A Rasp of Sand is created by David Cox, an awesome guy.
He's given me permission to public content as part of this open source project, to help facilitate running the game.
Please check out the Kickstarter project here: https://www.kickstarter.com/projects/dastardlydave/a-rasp-of-sand-a-roguelike-tabletop-rpg-experience

## Installation
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
...
```

![Imgur](https://i.imgur.com/u2BgBhV.png)

Please run `aros --help` to see a list of additional commands and arguments.
If you find any bugs, feel free to open an issue in this project, with as much detail as you can.

Happy RASPing!
