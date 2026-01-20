# Sales Analytics System

This project involves a Python-based Sales Analytics System that processes sales transaction data, performs validation and analysis, enriches data using an external product API, and generates a detailed analytics report.

# Repository Structure
sales-analytics-system/
  ├── README.md
  
  ├── main.py
  
  ├── utils/
  
  │   ├── file_handler.py
  │   ├── data_processor.py
  │   └── api_handler.py
  ├── data/
  │   └── sales_data.txt (provided)
  ├── output/
  └── requirements.txt


# Technologies Used
Python 3.x

# Outputs
- Enriched Sales Data: data/enriched_sales_data.txt

- Sales Analytics Report: output/sales_report.txt

## How to Run
1. Ensure Python 3.8+ is installed
2. Navigate to the project folder
3. Run in visual studio
   python main.py

## Project Structure
- main.py: Entry point
- utils/: Helper modules
- data/: Input sales data
- output/: Generated outputs

## Note to reviewer
In the provided sales data, the product id starts with 101,102... The json data has products with ids from 1 to 3. So there is no match in the records. Hence the API match returns false in the enrichedsalesdata.txt.
