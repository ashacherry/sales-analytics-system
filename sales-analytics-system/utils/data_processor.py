def calculate_total_revenue(transactions):
    total_revenue = 0.0

    for txn in transactions:
        try:
            total_revenue += txn["Quantity"] * txn["UnitPrice"]
        except (KeyError, TypeError):
            # Skip malformed transaction records safely
            continue

    return round(total_revenue, 2)

def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics

    Expected Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        ...
    }
    """

    region_stats = {}
    total_sales_all_regions = 0.0

    # ----------------------------------------
    # Aggregate sales and counts per region
    # ----------------------------------------
    for txn in transactions:
        try:
            region = txn["Region"]
            amount = txn["Quantity"] * txn["UnitPrice"]

            if region not in region_stats:
                region_stats[region] = {
                    "total_sales": 0.0,
                    "transaction_count": 0
                }

            region_stats[region]["total_sales"] += amount
            region_stats[region]["transaction_count"] += 1
            total_sales_all_regions += amount

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Calculate percentage contribution
    # ----------------------------------------
    for region in region_stats:
        if total_sales_all_regions > 0:
            percentage = (
                region_stats[region]["total_sales"] / total_sales_all_regions
            ) * 100
        else:
            percentage = 0.0

        region_stats[region]["percentage"] = round(percentage, 2)

        # Round total sales to 2 decimals for consistency
        region_stats[region]["total_sales"] = round(
            region_stats[region]["total_sales"], 2
        )

    # ----------------------------------------
    # Sort by total_sales (descending)
    # ----------------------------------------
    sorted_region_stats = dict(
        sorted(
            region_stats.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_stats

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples

    Expected Output Format:
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 19000.0),
        ...
    ]
    """

    product_stats = {}

    # ----------------------------------------
    # Aggregate quantity and revenue per product
    # ----------------------------------------
    for txn in transactions:
        try:
            product_name = txn["ProductName"]
            quantity = txn["Quantity"]
            revenue = quantity * txn["UnitPrice"]

            if product_name not in product_stats:
                product_stats[product_name] = {
                    "total_quantity": 0,
                    "total_revenue": 0.0
                }

            product_stats[product_name]["total_quantity"] += quantity
            product_stats[product_name]["total_revenue"] += revenue

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Convert to list of tuples
    # ----------------------------------------
    product_list = [
        (
            product,
            stats["total_quantity"],
            round(stats["total_revenue"], 2)
        )
        for product, stats in product_stats.items()
    ]

    # ----------------------------------------
    # Sort by total quantity sold (descending)
    # ----------------------------------------
    product_list.sort(key=lambda x: x[1], reverse=True)

    # ----------------------------------------
    # Return top n products
    # ----------------------------------------
    return product_list[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics

    Expected Output Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        ...
    }
    """

    customer_stats = {}

    # ----------------------------------------
    # Aggregate customer data
    # ----------------------------------------
    for txn in transactions:
        try:
            customer_id = txn["CustomerID"]
            product = txn["ProductName"]
            amount = txn["Quantity"] * txn["UnitPrice"]

            if customer_id not in customer_stats:
                customer_stats[customer_id] = {
                    "total_spent": 0.0,
                    "purchase_count": 0,
                    "products_bought": set()
                }

            customer_stats[customer_id]["total_spent"] += amount
            customer_stats[customer_id]["purchase_count"] += 1
            customer_stats[customer_id]["products_bought"].add(product)

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Final calculations per customer
    # ----------------------------------------
    for customer_id, stats in customer_stats.items():
        count = stats["purchase_count"]
        stats["avg_order_value"] = (
            round(stats["total_spent"] / count, 2) if count > 0 else 0.0
        )

        stats["total_spent"] = round(stats["total_spent"], 2)
        stats["products_bought"] = sorted(stats["products_bought"])

    # ----------------------------------------
    # Sort by total_spent (descending)
    # ----------------------------------------
    sorted_customers = dict(
        sorted(
            customer_stats.items(),
            key=lambda item: item[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customers

def daily_sales_trend(transactions):

    daily_stats = {}

    # ----------------------------------------
    # Aggregate data per date
    # ----------------------------------------
    for txn in transactions:
        try:
            date = txn["Date"]
            customer_id = txn["CustomerID"]
            amount = txn["Quantity"] * txn["UnitPrice"]

            if date not in daily_stats:
                daily_stats[date] = {
                    "revenue": 0.0,
                    "transaction_count": 0,
                    "unique_customers": set()
                }

            daily_stats[date]["revenue"] += amount
            daily_stats[date]["transaction_count"] += 1
            daily_stats[date]["unique_customers"].add(customer_id)

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Finalize daily statistics
    # ----------------------------------------
    for date, stats in daily_stats.items():
        stats["revenue"] = round(stats["revenue"], 2)
        stats["unique_customers"] = len(stats["unique_customers"])

    # ----------------------------------------
    # Sort chronologically by date
    # ----------------------------------------
    sorted_daily_stats = dict(sorted(daily_stats.items()))

    return sorted_daily_stats

def find_peak_sales_day(transactions):
   
    daily_totals = {}

    # ----------------------------------------
    # Aggregate revenue and count per date
    # ----------------------------------------
    for txn in transactions:
        try:
            date = txn["Date"]
            amount = txn["Quantity"] * txn["UnitPrice"]

            if date not in daily_totals:
                daily_totals[date] = {
                    "revenue": 0.0,
                    "transaction_count": 0
                }

            daily_totals[date]["revenue"] += amount
            daily_totals[date]["transaction_count"] += 1

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Identify peak sales day
    # ----------------------------------------
    peak_date = None
    peak_revenue = 0.0
    peak_txn_count = 0

    for date, stats in daily_totals.items():
        if stats["revenue"] > peak_revenue:
            peak_date = date
            peak_revenue = stats["revenue"]
            peak_txn_count = stats["transaction_count"]

    return (
        peak_date,
        round(peak_revenue, 2),
        peak_txn_count
    )

def low_performing_products(transactions, threshold=10):
    
    product_stats = {}

    # ----------------------------------------
    # Aggregate quantity and revenue per product
    # ----------------------------------------
    for txn in transactions:
        try:
            product = txn["ProductName"]
            quantity = txn["Quantity"]
            revenue = quantity * txn["UnitPrice"]

            if product not in product_stats:
                product_stats[product] = {
                    "total_quantity": 0,
                    "total_revenue": 0.0
                }

            product_stats[product]["total_quantity"] += quantity
            product_stats[product]["total_revenue"] += revenue

        except (KeyError, TypeError):
            # Skip malformed records safely
            continue

    # ----------------------------------------
    # Filter low-performing products
    # ----------------------------------------
    low_products = [
        (
            product,
            stats["total_quantity"],
            round(stats["total_revenue"], 2)
        )
        for product, stats in product_stats.items()
        if stats["total_quantity"] < threshold
    ]

    # ----------------------------------------
    # Sort by total quantity ascending
    # ----------------------------------------
    low_products.sort(key=lambda x: x[1])

    return low_products
