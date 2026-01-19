# utils/file_handler.py

from pathlib import Path
from datetime import datetime


# ----------- TASK 1.1 & 1.2 : READ DATA — HANDLE ENCODING -----------
def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues.

    Returns:
        lines (list): cleaned raw transaction lines (header removed)
        discarded (int): count of discarded lines (header + empty lines)
    """

    # Standardize reading from repo root
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / filename

    encodings = ["utf-8", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            with open(data_path, "r", encoding=enc) as file:
                raw_lines = file.readlines()

            total_lines = len(raw_lines)

            # Skip header + empty lines
            lines = [
                line.strip()
                for line in raw_lines[1:]
                if line.strip()
            ]

            discarded = total_lines - 1 - len(lines)
            return lines, discarded

        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise FileNotFoundError(f"Sales data not found: {data_path}")

    raise Exception("Unable to read file with supported encodings")


# ----------- TASK 1.2 : PARSE & CLEAN DATA -----------
def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries.
    """
    transactions = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        tid, date, pid, pname, qty, price, cid, region = parts

        # Clean product name (remove commas)
        pname = pname.replace(",", " ")

        try:
            quantity = int(qty)
            unit_price = float(price.replace(",", ""))
        except ValueError:
            continue

        transactions.append({
            "TransactionID": tid.strip(),
            "Date": date.strip(),
            "ProductID": pid.strip(),
            "ProductName": pname.strip(),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": cid.strip(),
            "Region": region.strip()
        })

    return transactions


# ----------- TASK 1.3 : VALIDATION & FILTERING -----------
def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.
    Displays regions, amount range, and counts after each filter.
    """

    valid = []
    invalid_count = 0

    for t in transactions:
        if (
            not t["TransactionID"].startswith("T") or
            not t["ProductID"].startswith("P") or
            not t["CustomerID"].startswith("C") or
            not t["Region"] or
            t["Quantity"] <= 0 or
            t["UnitPrice"] <= 0
        ):
            invalid_count += 1
            continue

        valid.append(t)

    # ---- FILTER DISPLAY (MANDATORY) ----
    regions = sorted(set(t["Region"] for t in valid))
    print(f"Regions: {', '.join(regions)}")

    amounts = [t["Quantity"] * t["UnitPrice"] for t in valid]
    min_amt, max_amt = min(amounts), max(amounts)
    print(f"Amount Range: ₹{int(min_amt)} - ₹{int(max_amt)}")

    filtered = valid
    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(filtered)
        filtered = [t for t in filtered if t["Region"] == region]
        filtered_by_region = before - len(filtered)
        print(f"After region filter: {len(filtered)} records")

    if min_amount is not None:
        before = len(filtered)
        filtered = [
            t for t in filtered
            if (t["Quantity"] * t["UnitPrice"]) >= min_amount
        ]
        filtered_by_amount += before - len(filtered)
        print(f"After min amount filter: {len(filtered)} records")

    if max_amount is not None:
        before = len(filtered)
        filtered = [
            t for t in filtered
            if (t["Quantity"] * t["UnitPrice"]) <= max_amount
        ]
        filtered_by_amount += before - len(filtered)
        print(f"After max amount filter: {len(filtered)} records")

    summary = {
        "total_input": len(transactions),
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered)
    }

    return filtered, invalid_count, summary
