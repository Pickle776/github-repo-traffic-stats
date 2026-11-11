import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
from datetime import datetime, timedelta
import os

def create_plot(views_df, clones_df, title, filename):
    current_date = datetime.now().date()
    start_date = current_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=current_date, freq='D').date

    df_full_views = pd.DataFrame(index=date_range)
    df_full_views['count'] = 0
    df_full_views['uniques'] = 0
    if views_df is not None and not views_df.empty:
        df_full_views.update(views_df)

    df_full_clones = pd.DataFrame(index=date_range)
    df_full_clones['count'] = 0
    df_full_clones['uniques'] = 0
    if clones_df is not None and not clones_df.empty:
        df_full_clones.update(clones_df)

    total_views = int(df_full_views["count"].sum())
    total_uniques = int(df_full_views["uniques"].sum())
    total_clones = int(df_full_clones["count"].sum())

    plt.figure(figsize=(12, 6))
    plt.plot(df_full_views.index, df_full_views["count"], label="Views", color='blue', linewidth=2)
    plt.plot(df_full_views.index, df_full_views["uniques"], label="Unique Visitors", color='red', linewidth=1.5)
    plt.plot(df_full_clones.index, df_full_clones["count"], label="Clones", color='green', linewidth=1.5, linestyle='--')

    plt.title(f"{title} ({total_views} Views, {total_uniques} Unique Visitors, {total_clones} Clones)")
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.legend()
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(filename, dpi=100, bbox_inches='tight', format='webp')
    plt.close()

def main():
    with open('github_username.txt', 'r', encoding='utf-8') as file:
        owner = file.read().strip()

    views_dir = 'data/github_views'
    clones_dir = 'data/github_clones'
    plots_dir = 'preview_plots'
    os.makedirs(plots_dir, exist_ok=True)

    if not os.path.exists(views_dir):
        return

    for filename in sorted(os.listdir(views_dir)):
        if filename.endswith('.csv'):
            repo = filename[:-4]
            views_df = None
            clones_df = None

            views_file = os.path.join(views_dir, filename)
            clones_file = os.path.join(clones_dir, filename)

            try:
                if os.path.isfile(views_file) and os.path.getsize(views_file) > 0:
                    views_df = pd.read_csv(views_file, parse_dates=['date'])
                    views_df.set_index(pd.to_datetime(views_df['date']).dt.date, inplace=True)
            except Exception as e:
                print(f"Error reading {views_file}: {e}")

            try:
                if os.path.isfile(clones_file) and os.path.getsize(clones_file) > 0:
                    clones_df = pd.read_csv(clones_file, parse_dates=['date'])
                    clones_df.set_index(pd.to_datetime(clones_df['date']).dt.date, inplace=True)
            except Exception as e:
                print(f"Error reading {clones_file}: {e}")

            plot_filename = f'{plots_dir}/{repo}.webp'
            create_plot(views_df, clones_df, f'{owner}/{repo}', plot_filename)
            print(f"Created plot for {owner}/{repo}")

if __name__ == "__main__":
    main()
