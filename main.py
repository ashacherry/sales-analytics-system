from pathlib import Path
from datetime import datetime
import sys

from utils.file_handler import (
    read_sales_data,
    parse_transactions,
    validate_and_filter
)
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    low_performing_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)


class Tee:
    """Redirect print output to a file only"""
    def __init__(self, file):
        self.file = file

    def write(self, data):
        self.file.write(data)

    def flush(self):
        self.file.flush()


def main():
    try:
        # ----------------------------------------
        # Setup output file (RESET each run)
        # ----------------------------------------
        base_dir = Path(__file__).resolve().parent
        output_dir = base_dir / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "output.txt"

        with open(output_file, "w", encoding="utf-8"):
            pass  # clear file

        # ========================================
        # TERMINAL OUTPUT (MUST NOT CHANGE)
        # ========================================
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()

        # ----------------------------------------
        # [1/10] Reading sales data
        # ----------------------------------------
        print("[1/10] Reading sales data...")
        raw_lines, discarded_read = read_sales_data("sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # ----------------------------------------
        # [2/10] Parsing and cleaning data
        # ----------------------------------------
        print("[2/10] Parsing and cleaning data...")
        parsed_txns, discarded_clean, discarded_records = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(parsed_txns)} records\n")

        # ----------------------------------------
        # [3/10] Filter Options Available
        # ----------------------------------------
        print("[3/10] Filter Options Available:")
        validate_and_filter(parsed_txns)
        print()

        choice = input("Do you want to filter data? (y/n): ").strip().lower()
        print()

        region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            region = input("Enter region (or press Enter to skip): ").strip() or None
            min_input = input("Enter minimum amount (or press Enter to skip): ").strip()
            min_amount = float(min_input) if min_input else None
            max_input = input("Enter maximum amount (or press Enter to skip): ").strip()
            max_amount = float(max_input) if max_input else None

        # ----------------------------------------
        # [4/10] Validating transactions
        # ----------------------------------------
        print("[4/10] Validating transactions...")
        valid_txns, invalid_count, _ = validate_and_filter(
            parsed_txns,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}\n")

        # ----------------------------------------
        # WRITE DISCARDED SUMMARY AT TOP OF FILE
        # ----------------------------------------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"{timestamp}\n")
            f.write(f"Read-level discarded: {discarded_read}\n")
            f.write(f"Cleaning-level discarded: {discarded_clean}\n")
            f.write(f"Validation-level invalid: {invalid_count}\n\n")

            f.write("Discarded Records:\n")
            for rec in discarded_records:
                f.write(rec + "\n")
            f.write("\n")

        # ----------------------------------------
        # [5/10] Analyzing sales data
        # ----------------------------------------
        print("[5/10] Analyzing sales data...")

        with open(output_file, "a", encoding="utf-8") as f:
            original_stdout = sys.stdout
            sys.stdout = Tee(f)

            print("=" * 60)
            print("SALES ANALYSIS RESULTS")
            print("=" * 60)

            total_revenue = calculate_total_revenue(valid_txns)
            print("Total Revenue:")
            print(total_revenue)
            print()

            print("Region-wise Sales:")
            region_stats = region_wise_sales(parsed_txns)
            print(region_stats)
            print()

            print("Top Selling Products:")
            top_products = top_selling_products(valid_txns)
            print(top_products)
            print()

            print("Peak Sales Day:")
            peak_day = find_peak_sales_day(parsed_txns)
            print(peak_day)
            print()

            print("Low Performing Products:")
            print(low_performing_products(valid_txns))
            print()

            print("Customer Analysis:")
            print(customer_analysis(valid_txns))
            print()

            print("Daily Sales Trend:")
            print(daily_sales_trend(parsed_txns))
            print()

            sys.stdout = original_stdout

        print("✓ Analysis complete\n")

        # ----------------------------------------
        # [6/10] Fetching product data from API
        # ----------------------------------------
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products\n")

        # ----------------------------------------
        # [7/10] Enriching sales data
        # ----------------------------------------
        print("[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_txns = enrich_sales_data(valid_txns, product_mapping)

        matched = sum(1 for t in enriched_txns if t.get("API_Match"))
        total = len(valid_txns)
        percent = (matched / total * 100) if total else 0

        print(f"✓ Enriched {matched}/{total} transactions ({percent:.1f}%)\n")

        # ----------------------------------------
        # [8/10] Saving enriched data
        # ----------------------------------------
        print("[8/10] Saving enriched data...")
        save_enriched_data(enriched_txns)
        print("✓ Saved to: data/enriched_sales_data.txt\n")

        # ----------------------------------------
        # [9/10] Generating report
        # ----------------------------------------
        print("[9/10] Generating report...")

        report_file = base_dir / "output" / "sales_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("SALES ANALYTICS REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write("VALIDATION SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Valid Transactions   : {len(valid_txns)}\n")
            f.write(f"Invalid Transactions : {invalid_count}\n\n")

            f.write("REVENUE SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Revenue : ₹{total_revenue}\n\n")

            f.write("REGION-WISE SALES\n")
            f.write("-" * 40 + "\n")
            for region, stats in region_stats.items():
                f.write(
                    f"{region}: ₹{stats['total_sales']} | "
                    f"Transactions: {stats['transaction_count']} | "
                    f"Contribution: {stats['percentage']}%\n"
                )
            f.write("\n")

            f.write("TOP SELLING PRODUCTS\n")
            f.write("-" * 40 + "\n")
            for product, qty, revenue in top_products:
                f.write(f"{product} | Qty: {qty} | Revenue: ₹{revenue}\n")
            f.write("\n")

            f.write("PEAK SALES DAY\n")
            f.write("-" * 40 + "\n")
            f.write(
                f"Date: {peak_day[0]} | "
                f"Revenue: ₹{peak_day[1]} | "
                f"Transactions: {peak_day[2]}\n\n"
            )

            f.write("API ENRICHMENT SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Matched Transactions : {matched}\n")
            f.write(f"Total Transactions   : {total}\n")
            f.write(f"Coverage             : {percent:.1f}%\n")

        print("✓ Report saved to: output/sales_report.txt\n")

    except Exception as e:
        print("An error occurred during execution")
        print(f"Reason: {e}")


if __name__ == "__main__":
    main()
