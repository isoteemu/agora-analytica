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
(.venv) $ python3 --debug cli.py build --method linear --limit 50
```

## Starting local development webserver

Windows ``command.com``

```cmd
> set FLASK_ENV=development
> set FLASK_APP=agora_analytica.flask:app
> flask run
```

Windows PowerShell

```ps

$env:FLASK_ENV = "development"
$env:FLASK_APP = "agora_analytica.flask:app"
flask run
```

Bash:

```bash
(.venv) $ FLASK_ENV=development FLASK_APP=agora_analytica.flask:app flask run
```
