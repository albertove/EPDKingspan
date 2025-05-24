# EPD Dashboard Application

A Streamlit-based web application for Environmental Product Declaration (EPD) calculations and comparisons. This application provides tools for product comparison, environmental impact calculations, and transport emissions assessment.

## Features

### 1. Comparison Tool
- Compare environmental impacts of different products
- Support for multiple product types (pipes, sleeves, valves)
- Sortable dimensions and environmental metrics
- Clear labeling for recase products
- Interactive data visualization

### 2. Project Calculator (A1-A3)
- Calculate environmental impacts for specific projects
- Support for multiple product types:
  - Pipes
  - Fittings
  - Sleeves
  - Valves
- Detailed breakdown of environmental metrics
- User-friendly interface for input parameters

### 3. Transport Calculator (A5)
- Calculate transport-related CO2 emissions
- Support for multiple transport modes:
  - Road transport (various truck types)
  - Maritime transport
  - Multi-modal transport combinations
- Interactive map visualization
- Real-time route calculation
- Detailed emissions breakdown

## Technical Requirements

- Python 3.8 or higher
- Streamlit
- Additional dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the application through your web browser at `http://localhost:8501`

3. Log in using your credentials

4. Navigate between different tools using the sidebar menu:
   - Comparison Tool
   - Project Calculator (A1-A3)
   - Transport Calculator (A5)

## Project Structure

```
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── config/
│   └── settings.py       # Application settings
├── views/
│   ├── comparison.py     # Comparison tool implementation
│   ├── calculator.py     # Project calculator implementation
│   ├── transport.py      # Transport calculator implementation
│   └── login.py         # Authentication module
└── utils/
    └── helpers.py        # Helper functions
```

## Features in Detail

### Comparison Tool
- Compare environmental metrics across different products
- Sort and filter products by various parameters
- Visual representation of environmental impacts
- Support for multiple product categories

### Project Calculator
- Calculate environmental impacts for specific projects
- Input validation and error handling
- Detailed breakdown of environmental metrics
- Support for multiple product types and configurations

### Transport Calculator
- Calculate CO2 emissions for transport routes
- Interactive map visualization using Folium
- Support for:
  - Road transport (various vehicle types)
  - Maritime transport
  - Multi-modal transport combinations
- Real-time route calculation and optimization
- Detailed emissions breakdown by transport leg

## Acknowledgments

- Developed for Kingspan
- Built with Streamlit
- Uses OpenStreetMap for mapping data
- Implements EPD calculation methodologies 