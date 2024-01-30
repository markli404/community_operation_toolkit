from github.github_util import *
from matplotlib import pyplot as plt

def plot_bar_graph(metric, days=None):
    df = load_history_df(metric)
    dates = [datetime.strptime(i, "%Y-%m-%d") for i in df['dates'].tolist()]
    counts = df['counts']
    cumulative_counts = [sum(counts[:i]) for i in range(len(counts))]

    fig, ax1 = plt.subplots(figsize=(13, 4))
    ax1.bar(dates, cumulative_counts, color="#8fd7d7", label=f'Total Number of {metric}')
    ax1.xaxis_date()
    ax1.set_xlabel('Date')
    ax1.legend([])

    ax2 = ax1.twinx()
    ax2.plot(dates, counts, color="#00b0be", label=f'Daily Increase in {metric}')

    fig.legend(loc="upper right")

    plt.title(f'Daily and Cumulative {metric} Trends for {owner} {repo} on GitHub')

    plt.show()