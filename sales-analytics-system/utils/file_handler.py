# import libraries
from pathlib import Path
from datetime import datetime


def read_sales_data(filename):

    # resolve project paths
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / filename

    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            # read entire file
            with open(data_path, "r", encoding=encoding) as file:
                raw_lines = file.readlines()

            total_lines = len(raw_lines)

            # skip header and remove empty lines
            lines = [
                line.strip()
                for line in raw_lines[1:]
                if line.strip()
            ]

            # header + empty lines removed
            discarded = total_lines - 1 - len(lines)

            return lines, discarded

        except UnicodeDecodeError:
            continue

        except FileNotFoundError:
            raise FileNotFoundError(f"Sales data not found: {data_path}")

    raise ValueError("Unable to read file with supported encodings")


# ---------------- TEST + LOGGING ----------------
if __name__ == "__main__":
    result, discarded = read_sales_data("sales_data.txt")

    print(f"Transactions read: {len(result)}")
    print(f"Transactions discarded: {discarded}")

    # write run info to output/output.txt
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "output.txt"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_name = Path(__file__).name

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(
            f"{timestamp} | {script_name} | "
            f"Transactions read: {len(result)} | "
            f"Discarded: {discarded}\n"
        )
def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    Removes invalid records as per data cleaning criteria

    Returns:
    - parsed_transactions
    - discarded_count
    - discarded_records (raw lines)
    """

    parsed_transactions = []
    discarded_records = []
    discarded_count = 0
    total_records = 0

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue

        total_records += 1
        parts = line.split("|")

        if len(parts) != 8:
            discarded_count += 1
            discarded_records.append(line)
            continue

        try:
            transaction_id = parts[0].strip()
            date = parts[1].strip()
            product_id = parts[2].strip()
            product_name = parts[3].replace(",", " ").strip()
            quantity = int(parts[4].replace(",", "").strip())
            unit_price = float(parts[5].replace(",", "").strip())
            customer_id = parts[6].strip()
            region = parts[7].strip()

            # INVALID RULES
            if not transaction_id.startswith("T"):
                raise ValueError("Invalid TransactionID")
            if not customer_id or not region:
                raise ValueError("Missing CustomerID or Region")
            if quantity <= 0:
                raise ValueError("Invalid Quantity")
            if unit_price <= 0:
                raise ValueError("Invalid UnitPrice")

            parsed_transactions.append({
                "TransactionID": transaction_id,
                "Date": date,
                "ProductID": product_id,
                "ProductName": product_name,
                "Quantity": quantity,
                "UnitPrice": unit_price,
                "CustomerID": customer_id,
                "Region": region
            })

        except Exception:
            discarded_count += 1
            discarded_records.append(line)

    # Required console output
    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {discarded_count}")
    print(f"Valid records after cleaning: {len(parsed_transactions)}")

    return parsed_transactions, discarded_count, discarded_records

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """

    total_input = len(transactions)
    invalid_count = 0
    valid_transactions = []

    # -----------------------------
    # VALIDATION
    # -----------------------------
    for txn in transactions:
        try:
            if txn["Quantity"] <= 0:
                invalid_count += 1
                continue
            if txn["UnitPrice"] <= 0:
                invalid_count += 1
                continue
            if not txn["TransactionID"].startswith("T"):
                invalid_count += 1
                continue
            if not txn["ProductID"].startswith("P"):
                invalid_count += 1
                continue
            if not txn["CustomerID"].startswith("C"):
                invalid_count += 1
                continue

            valid_transactions.append(txn)

        except Exception:
            invalid_count += 1
            continue

    # -----------------------------
    # FILTER DISPLAY (ALWAYS)
    # -----------------------------
    regions = sorted({t["Region"] for t in valid_transactions})
    print(f"Regions: {', '.join(regions)}")

    amounts = [t["Quantity"] * t["UnitPrice"] for t in valid_transactions]
    if amounts:
        print(f"Amount Range: ₹{min(amounts)} - ₹{max(amounts)}")

    # -----------------------------
    # APPLY FILTERS
    # -----------------------------
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered_transactions = valid_transactions

    if region:
        before = len(filtered_transactions)
        filtered_transactions = [
            t for t in filtered_transactions
            if t["Region"].lower() == region.lower()
        ]

        filtered_by_region = before - len(filtered_transactions)
        print(f"After region filter: {len(filtered_transactions)} records")

    if min_amount is not None or max_amount is not None:
        before = len(filtered_transactions)
        filtered_transactions = [
            t for t in filtered_transactions
            if (min_amount is None or t["Quantity"] * t["UnitPrice"] >= min_amount)
            and (max_amount is None or t["Quantity"] * t["UnitPrice"] <= max_amount)
        ]
        filtered_by_amount = before - len(filtered_transactions)
        print(f"After amount filter: {len(filtered_transactions)} records")

    # -----------------------------
    # SUMMARY
    # -----------------------------
    summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered_transactions)
    }

    return filtered_transactions, invalid_count, summary
