# Kingspan EPD Dashboard

A Streamlit-based dashboard for visualizing and analyzing Environmental Product Declaration (EPD) data for Kingspan products.

## Features

- Compare EPD data across different pipe series
- Interactive bar chart visualization
- Project CO2 calculator
- Support for both Single and Twin pipe types

## Project Structure

```
epd_dashboard/
├── data/                  # Excel data files
├── docs/                  # Documentation
├── src/                   # Source code
│   └── epd_dashboard/
│       ├── __init__.py
│       ├── app.py        # Main Streamlit application
│       ├── pages/        # Dashboard pages
│       └── utils/        # Utility functions
├── tests/                # Test files
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the dashboard:
```bash
streamlit run src/epd_dashboard/app.py
```

## Data Files

Place your Excel data files in the `data/` directory:
- EPD_singel_series_kingspan.xlsx
- EPD_twin_series_kingspan.xlsx 