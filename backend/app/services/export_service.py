import csv
import io
from typing import List, Dict, Any

def generate_csv_string(data: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        # Keep only specified keys, stringify dates
        cleaned_row = {
            k: str(row.get(k, "")) if row.get(k) is not None else ""
            for k in fieldnames
        }
        writer.writerow(cleaned_row)
    return output.getvalue()
