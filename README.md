# Streamlit Orders Dashboard

Interactive Streamlit dashboard for commercial performance analysis.

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

## Screenshot
Add one dashboard screenshot to strengthen the portfolio presentation:
- Save image as `assets/dashboard-overview.png`
- Recommended size: around 1600x900
- Add it below this section using:

```md
![Dashboard overview](assets/dashboard-overview.png)
```

## Publish on GitHub
1. Create a new public GitHub repository.
2. Push this folder.
3. Add a short repo description (example: `Streamlit dashboard for order analytics with schema validation`).
4. Add topic tags (example: `streamlit`, `python`, `data-visualization`, `dashboard`).
5. Pin the repo on your GitHub profile.

## CV link recommendation
Use the repository URL in your CV, for example:
- `https://github.com/<your-username>/streamlit-orders-dashboard`

Optional: deploy to Streamlit Community Cloud and include both links:
- Live app URL
- GitHub repo URL
