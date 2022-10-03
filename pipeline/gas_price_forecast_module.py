import argparse
import re

import altair as alt
import numpy as np
import pandas as pd
import requests
from statsforecast.models import AutoARIMA


def get_weekly_gas_price_data():
    response = requests.get(
        "https://www.eia.gov/petroleum/gasdiesel/xls/pswrgvwall.xls"
    )
    df = pd.read_excel(
        response.content,
        sheet_name="Data 12",
        index_col=0,
        skiprows=2,
        parse_dates=["Date"],
    ).rename(
        columns=lambda c: re.sub(
            "\(PADD 1[A-C]\)",
            "",
            c.replace("Weekly ", "").replace(
                " All Grades All Formulations Retail Gasoline Prices  (Dollars per Gallon)",
                "",
            ),
        ).strip()
    )
    return df


def get_weekly_gas_price_data_long(df):
    df_long = (
        df.reset_index()
        .melt(id_vars=["Date"], var_name="region", value_name="price")
        .rename(columns={"Date": "week"})
        .sort_values(["region", "week"])
        .assign(
            # if we're missing one value, just use the last value
            # (happens twice)
            price=lambda x: x["price"].combine_first(
                x.groupby("region")["price"].shift(1)
            ),
            # we'll forecast log(price) and then transform
            log_price=lambda x: np.log(x["price"]),
            # percentage price changes are approximately the difference in log(price)
            price_change=lambda x: (
                x["log_price"] - x.groupby("region")["log_price"].shift(1)
            ),
        )
        .query("price == price")  # filter out NAs
    )
    return df_long


def get_gas_price_forecast(cutoff_date, df_long, region):
    H = 13
    CI = 80
    width = 300
    height = 250
    plot_start_date = "2022-01-01"
    plot_title = f"{region} (as of {cutoff_date})"
    region_df = df_long.query(f"region == '{region}'")
    train = region_df.query(f"week < '{cutoff_date}'")
    m_aa = AutoARIMA()
    m_aa.fit(train["log_price"].values)
    raw_forecast = m_aa.predict(h=H, level=(CI,))
    raw_forecast_exp = {key: np.exp(value) for key, value in raw_forecast.items()}
    forecast = pd.DataFrame(raw_forecast_exp).assign(
        week=pd.date_range(train["week"].max(), periods=H, freq="W")
        + pd.Timedelta("7 days")
    )
    forecast = pd.concat(
        [
            forecast,
            train.tail(1)
            .rename(columns={"price": "mean"})
            .assign(
                **{f"lo-{CI}": lambda x: x["mean"], f"hi-{CI}": lambda x: x["mean"]}
            ),
        ]
    )
    uncertainty_plot = (
        forecast.pipe(alt.Chart, height=height, width=width)
        .encode(
            x="week",
            y=alt.Y(f"lo-{CI}", title="Price"),
            y2=alt.Y2(f"hi-{CI}", title="Price"),
        )
        .mark_area(opacity=0.2)
    )
    history_plot = (
        region_df.query(f"week >= '{plot_start_date}'")
        .pipe(alt.Chart, title=plot_title)
        .encode(x=alt.X("week", title="Week"), y=alt.Y("price", title="Price"))
        .mark_line()
    )
    forecast_plot = forecast.pipe(alt.Chart).encode(x="week", y="mean").mark_line()
    cutoff_plot = (
        train.tail(1).pipe(alt.Chart).encode(x="week").mark_rule(strokeDash=[10, 2])
    )
    full_plot = uncertainty_plot + history_plot + forecast_plot + cutoff_plot
    return full_plot


def run_session_including_weekly_gas_price_data(
    region="U.S.",
    cutoff_date="2022-10-02",
):
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    df = get_weekly_gas_price_data()
    artifacts["weekly_gas_price_data"] = copy.deepcopy(df)
    df_long = get_weekly_gas_price_data_long(df)
    artifacts["weekly_gas_price_data_long"] = copy.deepcopy(df_long)
    full_plot = get_gas_price_forecast(cutoff_date, df_long, region)
    artifacts["gas_price_forecast"] = copy.deepcopy(full_plot)
    return artifacts


def run_all_sessions(
    region="U.S.",
    cutoff_date="2022-10-02",
):
    artifacts = dict()
    artifacts.update(run_session_including_weekly_gas_price_data(region, cutoff_date))
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="U.S.")
    parser.add_argument("--cutoff_date", type=str, default="2022-10-02")
    args = parser.parse_args()
    artifacts = run_all_sessions(
        region=args.region,
        cutoff_date=args.cutoff_date,
    )
    print(artifacts)
