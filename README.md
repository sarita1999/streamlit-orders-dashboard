# Streamlit Orders Dashboard

Interactive Streamlit dashboard for order analytics with schema validation and interactive KPI visualizations.

## What this project shows
- End-to-end dashboard development in Python + Streamlit.
- KPI reporting and interactive filtering.
- Data-quality guardrails via strict schema validation.
- Flexible data source UX: bundled demo file or user upload.

## Quick start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data input
In the sidebar:
- Select `Use bundled demo (Orders.csv)` to run immediately.
- Or select `Upload your own CSV`.

Your CSV must include these columns:

`Row ID,Order ID,Order Date,Dispatch Date,Delivery Mode,Customer ID,Customer Name,Segment,City,State/Province,Country/Region,Region,Product ID,Category,Sub-Category,Product Name,Sales,Quantity,Discount,Profit`

If required columns are missing, the app stops and shows the missing column names.

## Repository structure
- `app.py`: dashboard app.
- `requirements.txt`: Python dependencies.
- `data/demo/Orders.csv`: bundled demo dataset.
- `data/template/orders_template.csv`: CSV template with required headers.
