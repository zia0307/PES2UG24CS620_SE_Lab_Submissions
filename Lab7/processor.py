def sanitize_meter_id(meter_id):
    """Strip whitespace and the characters ! @ # $ %, then uppercase.
    Returns an empty string for None / non-string input."""
    if not isinstance(meter_id, str):
        return ""
    meter_id = meter_id.strip()
    for ch in ['!', '@', '#', '$', '%']:
        meter_id = meter_id.replace(ch, '')
    return meter_id.upper()


def parse_consumption_readings(readings_csv):
    """Parse a comma-separated string of integers.
    Empty items and non-numeric items are skipped.
    Returns an empty list for None / non-string input."""
    if not isinstance(readings_csv, str):
        return []
    readings = []
    for item in readings_csv.split(','):
        item = item.strip()
        if not item:
            continue
        try:
            readings.append(int(item))
        except ValueError:
            continue
    return readings


def format_billing_summary(account_record):
    """Format 'Name:Usage:Zone' into a billing summary.
    Returns an error message instead of crashing on bad input."""
    if not isinstance(account_record, str):
        return "Invalid account record"
    parts = account_record.split(':')
    if len(parts) != 3:
        return "Invalid account record: expected Name:Usage:Zone"
    customer_name = parts[0].strip()
    zone = parts[2].strip()
    try:
        units = int(parts[1])
    except ValueError:
        return "Invalid account record: usage must be a whole number"
    if not customer_name or not zone:
        return "Invalid account record: name and zone are required"
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
