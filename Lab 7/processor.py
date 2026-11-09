def sanitize_meter_id(meter_id):
    if not isinstance(meter_id, str):
        return ""
    meter_id = meter_id.strip()
    for ch in ['!', '@', '#', '$', '%']:
        meter_id = meter_id.replace(ch, '')
    return meter_id.upper()

def parse_consumption_readings(readings_csv):
    if not isinstance(readings_csv, str):
        return []
    readings = readings_csv.split(',')
    parsed = []
    for r in readings:
        r = r.strip()
        if not r:
            continue
        try:
            parsed.append(int(r))
        except ValueError:
            continue
    return parsed

def format_billing_summary(account_record):
    if not isinstance(account_record, str):
        return "Invalid record: Expected string format"
    parts = account_record.split(':')
    if len(parts) < 3:
        return "Invalid record: Insufficient fields (Name:Usage:Zone required)"
    customer_name = parts[0].strip() or "Unknown"
    try:
        units = int(parts[1].strip())
    except ValueError:
        units = 0
    zone = parts[2].strip() or "Unknown"
    return f"Customer {customer_name} billed {units * 2} USD in {zone}"

def main():
    print("==== Running sanitize_meter_id ====")
    raw_id = input("Enter a meter ID with prefixes (!,@,#,$,%): ")
    clean_id = sanitize_meter_id(raw_id)
    print("Sanitized Meter ID:", clean_id)

    print("\n==== Running parse_consumption_readings ====")
    csv_input = input("Enter consumption readings (e.g. 10,25,30): ")
    readings_list = parse_consumption_readings(csv_input)
    print("Parsed Readings:", readings_list)

    print("\n==== Running format_billing_summary ====")
    summary_input = input("Enter account record (Name:Usage:Zone): ")
    summary = format_billing_summary(summary_input)
    print("Billing Summary:", summary)

if __name__ == "__main__":
    main()
