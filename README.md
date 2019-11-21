# AGORA ANALYTICA

## Setup
Create virtual environment in project root:
```bash
$ python3 -m virtualenv .venv
# On windows
$ .venv\Scripts\activate.bat
# On Bash
$ source .venv/bin/activate
```

Install dependencies:
```bash
(.venv) $ pip install -r requirements.txt
```

## Build
If data is not manually downloaded into `instance/` folder, script can automatically download and process it:
```bash
(.venv) $ python3 cli.py download
```

Calculate distances into `instance/` directory. Limit should be kept at reasonable low number for now.
```bash
(.venv) $ python3 cli.py build --limit 50
```

For testing purposes "dummy" method and debug might be preferred:
```bash
(.venv) $ python3 cli.py --debug build --limit 50 --method dummy
```

## Starting local development webserver:
```bash
(.venv) $ FLASK_ENV=development FLASK_APP=agora_analytica.flask:app flask run

(PS) $env:FLASK_ENV = "development"
     $env:FLASK_APP = "agora_analytica.flask:app"
     flask run
```
