# US Gas Prices Forecasting

This repository contains a Jupyter notebook which provides a forecast for US gas prices for the next 13 weeks (approximately one quarter) divided by regions. This forecast leverages three new packages:

1. `statsforecast` AutoARIMA implementation (built by Nixtla)
2. `LineaPy` for data and plot saving, as well as pipeline generation
3. `Quarto` for rendering documents from Jupyter notebooks

These packages have been used not only for their utility, but also for a hands-on exploration of their functionality.

## Dependencies
* Python
* statsforecast
* LineaPy
* Quarto
* pandas
* numpy
* scipy
* altair
* statsmodels
* requests
* re

## Installation
1. Clone this repository to your local machine.
2. Navigate to the cloned directory.
3. Install the necessary packages using pip:

```shell
pip install -r requirements.txt
```

## Usage
Run the notebook `forecast.ipynb` to see the US gas prices forecasting. The notebook downloads data from the EIA's website and performs data cleanup, exploration, and forecasting.

## Data Source
The data is sourced from [EIA's website](https://www.eia.gov/petroleum/gasdiesel/xls/pswrgvwall.xls) and consists of weekly gas prices by region since 1993. The data is saved as a LineaPy artifact for future usage.

## Data Exploration
The data is tidied and explored before forecasting. This includes:
- Converting from wide to long format.
- Renaming columns.
- Cleaning up missing values.
- Basic Exploratory Data Analysis (EDA).

## Forecasting
The `statsforecast` AutoARIMA implementation is used to forecast gas prices. As the forecast model does not handle seasonality well, the focus is on non-seasonal data.

## Automation
The notebook sets up a pipeline that can be scheduled to run regularly, allowing the forecast to be updated as new data comes in.

## License
MIT License. See [LICENSE](LICENSE) for more information.
