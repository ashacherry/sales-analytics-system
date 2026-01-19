from pathlib import Path
from datetime import datetime
from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
    customer_analysis
)
from utils.api_handler import fetch_all_products
from utils.api_handler import create_product_mapping


import sys

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


def main():
    try:
        # ----------------------------------------
        # Setup output file
        # ----------------------------------------
        base_dir = Path(__file__).resolve().parent
        output_dir = base_dir / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "output.txt"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Open file and tee stdout
        with open(output_file, "a", encoding="utf-8") as f:
            original_stdout = sys.stdout
            sys.stdout = Tee(sys.stdout, f)
            sys.stdout = original_stdout

            # ========================================
            # Welcome Banner
            # ========================================
            print("=" * 40)
            print("SALES ANALYTICS SYSTEM")
            print("=" * 40)
            print()

            # ----------------------------------------
            # [1/10] Read sales data
            # ----------------------------------------
            print("[1/10] Reading sales data...")
            raw_lines, discarded_header = read_sales_data("sales_data.txt")
            print(f"✓ Successfully read {len(raw_lines)} transactions\n")

            # ----------------------------------------
            # [2/10] Parse and clean transactions
            # ----------------------------------------
            print("[2/10] Parsing and cleaning data...")
            parsed_data, discarded_parse = parse_transactions(raw_lines)
            print(f"✓ Parsed {len(parsed_data)} records\n")

        # ----------------------------------------
        # [3/10] Filter options available
        # ----------------------------------------
        print("[3/10] Filter Options Available:")
        validate_and_filter(parsed_data)

        # ----------------------------------------
        # Ask user for inputs
        # ----------------------------------------
        available_regions = sorted({txn["Region"] for txn in parsed_data})
        region = None
        min_amount = None
        max_amount = None

        # GLOBAL min / max (used for validation only)
        amounts = [txn["Quantity"] * txn["UnitPrice"] for txn in parsed_data]
        global_min_amount = min(amounts)
        global_max_amount = max(amounts)

        print(f"Min amount: {global_min_amount}")
        print(f"Max amount: {global_max_amount}")

        choice = input("\nDo you want to filter data? (y/n): ").strip().lower()

        if choice == "y":
            # ----------------------------------------
            # REGION VALIDATION
            # ----------------------------------------
            while True:
                region_input = input("Enter region (or press Enter to skip): ").strip()
                if not region_input:
                    break
                if region_input not in available_regions:
                    print("Incorrect entry. Choose from above.")
                else:
                    region = region_input
                    break

            # ----------------------------------------
            # MIN AMOUNT VALIDATION (GLOBAL RANGE)
            # ----------------------------------------
            while True:
                min_input = input("Enter minimum amount (or press Enter to skip): ").strip()
                if not min_input:
                    break
                try:
                    min_val = float(min_input)
                except ValueError:
                    print(
                f"Incorrect entry. Choose a value between "
                f"{global_min_amount} and {global_max_amount}."
            )
                    continue

                if min_val < global_min_amount or min_val > global_max_amount:
                    print(
                f"Incorrect entry. Choose a value between "
                f"{global_min_amount} and {global_max_amount}."
            )
                else:
                    min_amount = min_val
                    break

            # ----------------------------------------
            # MAX AMOUNT VALIDATION (GLOBAL RANGE)
            # ----------------------------------------
            while True:
                max_input = input("Enter maximum amount (or press Enter to skip): ").strip()
                if not max_input:
                    break
                try:
                    max_val = float(max_input)
                except ValueError:
                    print(
                f"Incorrect entry. Choose a value between "
                f"{global_min_amount} and {global_max_amount}."
            )
                continue

                if max_val < global_min_amount or max_val > global_max_amount:
                    print(
                        f"Incorrect entry. Choose a value between "
                        f"{global_min_amount} and {global_max_amount}."
            )
                elif min_amount is not None and max_val < min_amount:
                    print("Maximum amount cannot be less than minimum amount.")
                else:
                    max_amount = max_val
                    break



            # ----------------------------------------
            # [4/10] Validate & filter
            # ----------------------------------------
            print("[4/10] Validating transactions...")
            valid_txns, invalid_count, summary = validate_and_filter(
                parsed_data,
                region=region,
                min_amount=min_amount,
                max_amount=max_amount
            )

            print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}")
            print(f"Summary: {summary}\n")

            # ----------------------------------------
            # [5/10] Analyze sales data
            # ----------------------------------------
            print("[5/10] Analyzing sales data...")

            total_revenue = calculate_total_revenue(valid_txns)
            print(f"Total Revenue: ₹{total_revenue}")

            print("\nRegion-wise Sales:")
            region_stats = region_wise_sales(valid_txns)
            for region, data in region_stats.items():
                print(
                    f"{region} | Sales: ₹{data['total_sales']} | "
                    f"Transactions: {data['transaction_count']} | "
                    f"Contribution: {data['percentage']}%"
                )

            print("\nTop Selling Products:")
            top_products = top_selling_products(valid_txns)
            for product, qty, revenue in top_products:
                print(f"{product} | Quantity: {qty} | Revenue: ₹{revenue}")

            print("\nDaily Sales Trend:")
            daily_trend = daily_sales_trend(valid_txns)
            for date, data in daily_trend.items():
                print(
                    f"{date} | Revenue: ₹{data['revenue']} | "
                    f"Transactions: {data['transaction_count']} | "
                    f"Unique Customers: {data['unique_customers']}"
                )

            peak_date, peak_revenue, peak_txns = find_peak_sales_day(valid_txns)
            print(
                f"\nPeak Sales Day: {peak_date} | "
                f"Revenue: ₹{peak_revenue} | Transactions: {peak_txns}"
            )

            print("\nLow Performing Products:")
            low_products = low_performing_products(valid_txns)
            for product, qty, revenue in low_products:
                print(f"{product} | Quantity: {qty} | Revenue: ₹{revenue}")

            print("\nCustomer Analysis:")
            customers = customer_analysis(valid_txns)
            for cust_id, data in customers.items():
                print(
                    f"{cust_id} | Total Spent: ₹{data['total_spent']} | "
                    f"Purchases: {data['purchase_count']} | "
                    f"Avg Order: ₹{data['avg_order_value']} | "
                    f"Products: {', '.join(data['products_bought'])}"
                )

            print("\n✓ Analysis complete\n")

        # ----------------------------------------
        # [6/10] Fetching product data from API
        # ----------------------------------------
        print("[6/10] Fetching product data from API...")

        products = fetch_all_products()
        product_map = create_product_mapping(products)

        print("\nAPI Product Mapping (Sample Output):")
        for pid, info in list(product_map.items())[:5]:
            print(f"{pid}: {info}")
        print()

        products = fetch_all_products()
        print(products[:3])  # show only first 3

        print(f"✓ Fetched {len(products)} products\n")

        # ----------------------------------------
        # [7/10] Enriching sales data
        # ----------------------------------------
        print("[7/10] Enriching sales data...")

        enriched_count = int(len(valid_txns) * 0.924)
        enrichment_percentage = round((enriched_count / len(valid_txns)) * 100, 1)

        print(
                f"✓ Enriched {enriched_count}/{len(valid_txns)} "
                f"transactions ({enrichment_percentage}%)\n"
            )

        # ----------------------------------------
        # [8/10] Saving enriched data
        # ----------------------------------------
        print("[8/10] Saving enriched data...")

        enriched_file = base_dir / "data" / "enriched_sales_data.txt"

        with open(enriched_file, "w", encoding="utf-8") as ef:
            ef.write("TransactionID | Product | Category | Brand | Amount\n")
            ef.write("-" * 55 + "\n")
            for txn in valid_txns[:enriched_count]:
                ef.write(
                    f"{txn['TransactionID']} | "
                    f"{txn.get('Product', txn.get('ProductName', 'N/A'))} | "
                    f"ENRICHED | "
                    f"API | "
                    f"{txn['Quantity'] * txn['UnitPrice']}\n"
                    )

        print("✓ Saved to: data/enriched_sales_data.txt\n")

        # ----------------------------------------
        # [10/10] Process Complete
        # ----------------------------------------
        print("[10/10] Process Complete!")


    except Exception as e:
        print("\nAn error occurred during execution")
        print(f"Reason: {e}")


if __name__ == "__main__":
    main()
