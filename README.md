# AGORA ANALYTICA

## Setup
Create virtual environment in project root:
```bash
$ python3 -m virtualenv .venv
# On windows
$ .venv\Scripts\activate.bat
# On Bash
$ source .venv/Scripts/activate
```

Install dependencies:
```bash
(.venv) $ pip install -r requirements.txt
```

## Build
If data is not manually downloaded into `instance/` folder, script can automaticly download and process it:
```bash
(.venv) $ python3 cli.py download
```

Build static page into `instance/` directory. Limit should be kept at reasonable low number for now.
```bash
(.venv) $ python3 cli.py build --limit 50
```
