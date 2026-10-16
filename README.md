
# Delivery Analytics Dashboard

## Project Overview
A Python-based delivery analytics project that analyzes synthetic delivery data to understand delivery status, delays, on-time performance, and regional performance.

## Technologies Used
- Python
- Pandas and NumPy
- SQL and SQLite
- Streamlit
- Data validation and testing

## Key Features
- Delivery status analysis
- On-time delivery rate calculation
- Average delivery delay analysis
- Regional performance comparison
- Interactive dashboard and filters
- SQL-based analytics
- CSV data export

## Project Workflow
1. Generate synthetic delivery data.
2. Inspect and validate the data.
3. Clean the data using a Python ETL pipeline.
4. Run data-quality tests.
5. Load cleaned records into SQLite.
6. Analyze delivery performance through SQL and Streamlit.

## How to Run

Install the dependencies:

```bash
pip install -r requirements.txt
```

Generate the data:

```bash
python src/generate_data.py
```

Run the ETL pipeline:

```bash
python src/etl_pipeline.py
```

Run the tests:

```bash
python tests/test_pipeline.py
```

Load the database:

```bash
python src/load_to_sqlite.py
```

Start the dashboard:

```bash
python -m streamlit run dashboard/app.py
```

## Data Note
This project uses synthetic data generated for learning and demonstration. It does not represent actual Amazon delivery operations.
<img width="1743" height="757" alt="image" src="https://github.com/user-attachments/assets/4cafc6bc-8ea9-4708-add7-baf1b7bf44d5" />
