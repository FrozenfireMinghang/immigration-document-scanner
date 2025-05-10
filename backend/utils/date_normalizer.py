import re
from difflib import get_close_matches

MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
}

def fix_month_string(raw_month_str):
    """
    Cleans and corrects the raw month string using fuzzy matching.
    For example, 'J EN' or 'AOUG' will be corrected to 'JAN' or 'AUG'.
    """
    cleaned = re.sub(r'[^A-Z]', '', raw_month_str.upper())
    matches = get_close_matches(cleaned, MONTH_MAP.keys(), n=1, cutoff=0.4)
    return MONTH_MAP[matches[0]] if matches else None

def normalize_single_date(date_str):
    """
    Converts a date string like '14 AOUG 23' to '14/08/2023'.
    Leaves 'dd/mm/yyyy' strings unchanged.
    """
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        return date_str

    parts = re.findall(r'\d{1,4}|[A-Z]+', date_str.upper())
    if len(parts) < 3:
        return date_str

    day = parts[0].zfill(2)
    raw_month = ''.join(parts[1:-1])
    month = fix_month_string(raw_month)
    year = parts[-1]

    # Fix 2-digit year like '23' to '2023'
    if len(year) == 2:
        year = '20' + year

    if month:
        return f"{day}/{month}/{year}"
    else:
        return date_str

def normalize_date_fields(data):
    """
    Normalizes the date format for specified keys in the dictionary.
    """
    date_keys = ['date_of_birth', 'issue_date', 'expiration_date']
    for key in date_keys:
        if key in data:
            data[key] = normalize_single_date(data[key])
    return data
