import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def plot_pr_graph(csv_path, start_date=None, end_date=None,
                  base_budget=73.9, annual_drop=0.8):

    # --- Step 1: Load and prepare the data ---
    data = pd.read_csv(csv_path, parse_dates=['Date'])
    data = data.sort_values('Date').reset_index(drop=True)

    # filter by date if range is provided
    if start_date:
        data = data[data['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data['Date'] <= pd.to_datetime(end_date)]

    if data.empty:
        raise ValueError("No data available in the given date range.")

    # --- Step 2: Calculate 30-day moving average ---
    data['PR_MA30'] = data['PR'].rolling(window=30, min_periods=1).mean()

    # --- Step 3: Create a yearly decaying budget line ---
    # Each year, the target budget drops by 0.8% from the previous year

    def fiscal_year(d):
        return d.year if d.month >= 7 else d.year - 1

    start_year = fiscal_year(data['Date'].min())
    data['FiscalYear'] = data['Date'].apply(fiscal_year)
    data['YearGap'] = data['FiscalYear'] - start_year
    data['Budget'] = base_budget * (1 - annual_drop/100) ** data['YearGap']

    # --- Step 4: Assign colors based on GHI ---
    def ghi_to_color(ghi):
        if ghi < 2:
            return 'navy'
        elif ghi < 4:
            return 'deepskyblue'
        elif ghi < 6:
            return 'orange'
        else:
            return 'brown'

    data['Color'] = data['GHI'].apply(ghi_to_color)

    # --- Step 5: Plot setup ---
    plt.figure(figsize=(15, 8))

    # daily PR scatter points
    plt.scatter(data['Date'], data['PR'], c=data['Color'], s=15, label='Daily PR')

    # 30-day average line
    plt.plot(data['Date'], data['PR_MA30'], color='red', linewidth=2.5, label='30-day moving average')

    # budget line (dark green)
    plt.plot(data['Date'], data['Budget'], color='darkgreen', linewidth=2, label='Target Budget Yield PR')

    # highlight points above budget
    above_points = data[data['PR'] > data['Budget']]
    plt.scatter(above_points['Date'], above_points['PR'],
                facecolors='none', edgecolors='black', s=40,
                label='Points Above Target Budget PR')

    above_ratio = (len(above_points) / len(data)) * 100

    # --- Step 6: Summary / stats box ---
    averages = {
        "7d": data['PR'].tail(7).mean(),
        "30d": data['PR'].tail(30).mean(),
        "60d": data['PR'].tail(60).mean(),
        "overall": data['PR'].mean()
    }

    info_box = (
        f"Avg PR (7 days):   {averages['7d']:.1f}%\n"
        f"Avg PR (30 days):  {averages['30d']:.1f}%\n"
        f"Avg PR (60 days):  {averages['60d']:.1f}%\n"
        f"Overall PR:        {averages['overall']:.1f}%\n"
        f"Above Target Points:\n{len(above_points)}/{len(data)} = {above_ratio:.1f}%"
    )

    # --- Step 7: Styling and layout ---
    plt.title('Performance Ratio Trend', fontsize=15, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Performance Ratio [%]')
    plt.ylim(0, 100)

    # format x-axis to show months properly
    start_month = datetime(data['Date'].min().year, data['Date'].min().month, 1)
    end_month = datetime(data['Date'].max().year, data['Date'].max().month, 1) + timedelta(days=31)
    plt.xlim(start_month, end_month)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

    # place stats box on plot
    plt.text(data['Date'].max() - timedelta(days=160), 10, info_box,
             fontsize=10, bbox=dict(facecolor='white', alpha=0.85))

    plt.legend(loc='upper left', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig("performance_ratio_graph.png", dpi=300, bbox_inches='tight')
    plt.show()
# Example call
plot_pr_graph("merged_PR_GHI.csv", start_date="2019-07-01", end_date="2022-03-24")
