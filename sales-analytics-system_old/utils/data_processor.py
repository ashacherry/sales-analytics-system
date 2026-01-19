def calculate_total_revenue(transactions):
    total_revenue = 0.0

    for txn in transactions:
        total_revenue += txn["Quantity"] * txn["UnitPrice"]

    return round(total_revenue, 2)

def region_wise_sales(transactions):
    region_data = {}
    grand_total = 0.0

    # Aggregate sales and transaction counts
    for txn in transactions:
        region = txn["Region"]
        sale_value = txn["Quantity"] * txn["UnitPrice"]

        if region not in region_data:
            region_data[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_data[region]["total_sales"] += sale_value
        region_data[region]["transaction_count"] += 1
        grand_total += sale_value

    # Calculate percentage contribution
    for region in region_data:
        region_data[region]["percentage"] = round(
            (region_data[region]["total_sales"] / grand_total) * 100, 2
        )

        region_data[region]["total_sales"] = round(
            region_data[region]["total_sales"], 2
        )

    # Sort by total_sales (descending)
    sorted_region_data = dict(
        sorted(
            region_data.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_data

def top_selling_products(transactions, n=5):
    product_data = {}

    # Aggregate quantity and revenue per product
    for txn in transactions:
        product = txn["ProductName"]
        quantity = txn["Quantity"]
        revenue = txn["Quantity"] * txn["UnitPrice"]

        if product not in product_data:
            product_data[product] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_data[product]["total_quantity"] += quantity
        product_data[product]["total_revenue"] += revenue

    # Sort by total quantity sold (descending)
    sorted_products = sorted(
        product_data.items(),
        key=lambda item: item[1]["total_quantity"],
        reverse=True
    )

    # Prepare result and limit to top n
    result = []
    for product, data in sorted_products[:n]:
        result.append(
            (
                product,
                data["total_quantity"],
                round(data["total_revenue"], 2)
            )
        )

    return result
def customer_analysis(transactions):
    customer_data = {}

    # Aggregate customer metrics
    for txn in transactions:
        customer_id = txn["CustomerID"]
        product = txn["ProductName"]
        order_value = txn["Quantity"] * txn["UnitPrice"]

        if customer_id not in customer_data:
            customer_data[customer_id] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products": set()
            }

        customer_data[customer_id]["total_spent"] += order_value
        customer_data[customer_id]["purchase_count"] += 1
        customer_data[customer_id]["products"].add(product)

    # Prepare final output and sort by total_spent (descending)
    sorted_customers = dict(
        sorted(
            customer_data.items(),
            key=lambda item: item[1]["total_spent"],
            reverse=True
        )
    )

    result = {}

    for customer_id, data in sorted_customers.items():
        avg_order_value = data["total_spent"] / data["purchase_count"]

        result[customer_id] = {
            "total_spent": round(data["total_spent"], 2),
            "purchase_count": data["purchase_count"],
            "avg_order_value": round(avg_order_value, 2),
            "products_bought": sorted(list(data["products"]))
        }

    return result

def daily_sales_trend(transactions):
    daily_data = {}

    # Aggregate daily metrics
    for txn in transactions:
        date = txn["Date"]          # expected format: YYYY-MM-DD
        revenue = txn["Quantity"] * txn["UnitPrice"]
        customer_id = txn["CustomerID"]

        if date not in daily_data:
            daily_data[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "customers": set()
            }

        daily_data[date]["revenue"] += revenue
        daily_data[date]["transaction_count"] += 1
        daily_data[date]["customers"].add(customer_id)

    # Prepare final output and sort chronologically
    sorted_daily_data = {}

    for date in sorted(daily_data.keys()):
        sorted_daily_data[date] = {
            "revenue": round(daily_data[date]["revenue"], 2),
            "transaction_count": daily_data[date]["transaction_count"],
            "unique_customers": len(daily_data[date]["customers"])
        }

    return sorted_daily_data
def find_peak_sales_day(transactions):
    daily_totals = {}

    # Aggregate revenue and transaction count per day
    for txn in transactions:
        date = txn["Date"]          # expected format: YYYY-MM-DD
        revenue = txn["Quantity"] * txn["UnitPrice"]

        if date not in daily_totals:
            daily_totals[date] = {
                "revenue": 0.0,
                "transaction_count": 0
            }

        daily_totals[date]["revenue"] += revenue
        daily_totals[date]["transaction_count"] += 1

    # Find peak sales day
    peak_date, peak_data = max(
        daily_totals.items(),
        key=lambda item: item[1]["revenue"]
    )

    return (
        peak_date,
        round(peak_data["revenue"], 2),
        peak_data["transaction_count"]
    )
def low_performing_products(transactions, threshold=10):
    product_data = {}

    # Aggregate quantity and revenue per product
    for txn in transactions:
        product = txn["ProductName"]
        quantity = txn["Quantity"]
        revenue = txn["Quantity"] * txn["UnitPrice"]

        if product not in product_data:
            product_data[product] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_data[product]["total_quantity"] += quantity
        product_data[product]["total_revenue"] += revenue

    # Filter products below threshold
    low_products = [
        (
            product,
            data["total_quantity"],
            round(data["total_revenue"], 2)
        )
        for product, data in product_data.items()
        if data["total_quantity"] < threshold
    ]

    # Sort by total quantity (ascending)
    low_products.sort(key=lambda item: item[1])

    return low_products
