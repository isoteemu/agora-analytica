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
```bash
(.venv) $ python3 cli.py build --limit 50
```
