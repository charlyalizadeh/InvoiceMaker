from datetime import datetime
from docx import Document
from icalendar import Calendar
from jinja2 import Template
import argparse
import calendar as cl
import pypandoc
import yaml
import warnings


def get_event_duration(calendar, start=None, end=None, by='TITLE'):
    events_duration = {}
    start = datetime.min if start is None else start
    end = datetime.max if end is None else end
    for event in calendar.events:
        dt_start = event["DTSTART"].dt
        dt_end = event["DTEND"].dt
        if dt_end < start or dt_start > end:
            continue
        if dt_start < start:
            dt_start = start
        if dt_end > dt_end:
            dt_end = end
        if event[by] not in events_duration.keys():
            events_duration[event[by]] = event["DTEND"].dt - event["DTSTART"].dt
        else:
            events_duration[event[by]] += event["DTEND"].dt - event["DTSTART"].dt
    return events_duration

def generate_services(calendar, start, end, services_price, by='TITLE'):
    services = []
    event_duration_month = get_event_duration(calendar, start, end, by=by)
    for event_name, duration in event_duration_month.items():
        duration_hour = duration.total_seconds() / 3600
        if event_name not in services_price:
            warnings.warn(f"{event_name} not in the config, assigning its price to 0.")
        service_price = services_price.get(event_name, 0)
        service_total = duration_hour * service_price
        services.append({
            "name": event_name,
            "quantity": duration_hour,
            "price": service_price,
            "total": service_price * duration_hour
        })
    return services

def generate_invoice(invoice, contract, company, client, template, services, date=None, **kwargs):
    date = date if date is not None else datetime.now().strftime("%d/%m/%Y")
    total = sum([s["total"] for s in services])
    data = {
        "invoice": invoice,
        "contract": contract,
        "company": company,
        "client": client,
        "services": services,
        "total": total,
        "date": date
    }
    invoice_filled = Template(template).render(**data)
    return invoice_filled

def print_event_duration(calendar, start, end):
    events_duration = get_event_duration(calendar, start=start, end=end)
    for event_name, duration in events_duration.items():
        print(f"{event_name}: {duration}h")

def render_invoice_docx(config, template):
    Path("results").mkdir(parents=True, exist_ok=True)
    services_price = {s["name"]: s["price"] for s in config["service"]}
    services_price = services_price
    services = generate_services(calendar, config["invoice"]["start"], config["invoice"]["end"], services_price)
    invoice_filled = generate_invoice(config["invoice"], config["contract"], config["company"], config["client"], template, services)
    invoice_filled = invoice_filled.encode('utf-8').decode('utf-8')
    outputfile_docx = f"results/invoice_{config['invoice']['id']}.docx"
    pypandoc.convert_text(
            invoice_filled,
            "docx",
            format="latex",
            outputfile=outputfile_docx,
            extra_args=['--standalone', '--reference-doc=custom-reference.docx']
    )

    # Apply table style
    doc = Document(outputfile_docx)
    table_style = "Table Grid"
    for table in doc.tables:
        table.style = table_style
    doc.save(outputfile_docx)

def parse_date(date):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass
    raise ValueError(f"Date {date} is not in a YAML format. Either use %Y-%m-%d or %Y-%m-%dT%H:%M:%S")

if __name__ == "__main__":
    pypandoc.download_pandoc()
    parser = argparse.ArgumentParser(
                prog="InvoiceMaker",
                description="Tool to make invoice from an iCalendar ics file"
    )
    parser.add_argument("calendar")
    parser.add_argument("--config", default="configs/config_exemple.yaml")
    parser.add_argument("--template", default="templates/invoice.tex.j2")
    parser.add_argument("--start", type=parse_date)
    parser.add_argument("--end", type=parse_date)
    parser.add_argument("--no-invoice", action="store_true", help="If set, won't generate an invoice and just display the time sum of the events in the calendar")
    args = parser.parse_args()

    with open(args.calendar, 'r') as file:
        ics_content = file.read()
    calendar = Calendar.from_ical(ics_content)

    with open(args.config) as file:
        config = yaml.safe_load(file)
    with open(args.template) as file:
        template = file.read()

    # CLI passed start and end date takes precedence over the yaml config
    if args.start:
        config["invoice"]["start"] = args.start
    if args.end:
        config["invoice"]["end"] = args.end

    if args.no_invoice:
        print_event_duration(calendar, config["invoice"]["start"], config["invoice"]["end"])
    else:
        render_invoice_docx(config, template)
