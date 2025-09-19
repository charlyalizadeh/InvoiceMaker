# InvoiceMaker

Simple tool to make invoice from .ics files.

## Setup

1. Install the requirements (I use venv but use whatever you want), pandoc will be installed using `pypandoc.download_pandoc`

```bash
python -m venv .venv
# Linux/MacOS
source .venv/bin/activate
# Windows
# .venv\Scripts\Activate
pip install -r requirements.txt
```

## Simple time computation

This script can be used to just compute the time of each element in the `.ics` file without generating an invoice:
```bash
python src/main.py my_calendar.ics --no-invoice
```
You can pass start and end date as arguments (instead as `invoice` subkeys in the config),
it will take the precedence over the yaml config:

```bash
python src/main.py my_calendar.ics --no-invoice \
                                   --start 2025-09-01 \
                                   --end 2025-12-31
# Or with the hours:
# python src/main.py my_calendar.ics --no-invoice \
#                                    --start 2025-09-01T00:00:00 \
#                                    --end 2025-12-31T:23:59:59
```

## Invoice generation


1. Setup the configuration information about your company and the client company (the exemple here is for the french system)

```yaml
company:
  name: "Company"
  owner: "Company owner"
  address: "Company address"
  mail: "company@exemple.com"
  siren: "XXX XXX XXX"
  ape_code: "XX.XX"
client:
  name: "Client"
  address: "Client address"
  siren: "XXX XXX XX"
contract:
  id: "Contract id"
service:
  -
    name: "Service 1"
    price: 50.5
  -
    name: "Service 2"
    price: 40.2
invoice:
  id: "Invoice id"
  start: 2025-09-01T00:00:00
  end: 2025-10-31T23:59:00
```

3. Optionally you can setup your own jinja template, see `/templates/invoice.tex.j2` for the default one
4. Run the script:
```bash
python src/main.py my_calendar.ics --config my_config.yaml
# Or with a custom template:
# python src/main.py my_calendar.ics --config my_config.yaml --template my_template.tex.j2
```
