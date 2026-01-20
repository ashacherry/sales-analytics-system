import requests
from pathlib import Path
def fetch_all_products():

    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get("products", [])

        print("✓ Successfully fetched products from API")
        return products

    except requests.exceptions.RequestException as e:
        print("✗ Failed to fetch products from API")
        print(f"Reason: {e}")
        return []

def create_product_mapping(api_products):
   

    product_map = {}

    for product in api_products:
        try:
            product_id = product.get("id")
            if product_id is None:
                continue

            product_map[product_id] = {
                "title": product.get("title"),
                "category": product.get("category"),
                "brand": product.get("brand"),
                "rating": product.get("rating")
            }

        except AttributeError:
            # In case product is not a dictionary
            continue

    return product_map

def enrich_sales_data(transactions, product_mapping):
  
    enriched_transactions = []

    for txn in transactions:
        # Start with a shallow copy of the transaction
        enriched_txn = txn.copy()

        # Default API fields
        enriched_txn["API_Category"] = None
        enriched_txn["API_Brand"] = None
        enriched_txn["API_Rating"] = None
        enriched_txn["API_Match"] = False

        try:
            product_id_raw = txn.get("ProductID")

            if product_id_raw:
                # Extract numeric part: P101 -> 101, P5 -> 5
                numeric_id_str = "".join(filter(str.isdigit, product_id_raw))

                if numeric_id_str:
                    numeric_id = int(numeric_id_str)

                    if numeric_id in product_mapping:
                        api_info = product_mapping[numeric_id]

                        enriched_txn["API_Category"] = api_info.get("category")
                        enriched_txn["API_Brand"] = api_info.get("brand")
                        enriched_txn["API_Rating"] = api_info.get("rating")
                        enriched_txn["API_Match"] = True

        except Exception:
            # Graceful failure: keep defaults
            pass

        enriched_transactions.append(enriched_txn)

    return enriched_transactions

from pathlib import Path

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file
    """

    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    header = (
        "TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|"
        "CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(header)

        # Write each transaction
        for txn in enriched_transactions:
            line = (
                f"{txn.get('TransactionID', '')}|"
                f"{txn.get('Date', '')}|"
                f"{txn.get('ProductID', '')}|"
                f"{txn.get('ProductName', '')}|"
                f"{txn.get('Quantity', '')}|"
                f"{txn.get('UnitPrice', '')}|"
                f"{txn.get('CustomerID', '')}|"
                f"{txn.get('Region', '')}|"
                f"{txn.get('API_Category') or ''}|"
                f"{txn.get('API_Brand') or ''}|"
                f"{txn.get('API_Rating') or ''}|"
                f"{txn.get('API_Match')}\n"
            )
            f.write(line)
