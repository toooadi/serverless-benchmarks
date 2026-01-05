import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

CSV_REL_PATH = os.path.join(
    # "210.thumbnailer_warm_cold_128_256_512_1024_2048_python_codepackage",
    "perf-cost",
    "python_311_large_perf-cost_256_1024_2048",
    "perf-cost",
    "result.csv"
)

LANGUAGE_NAME = "Python 3.11"
LANGUAGE_NAME_SAFE = "python3.11"
BENCHMARK_NAME = "311.compression"
TITLE_COMMENT = "container"


sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.figsize': (8, 6)})

def get_save_path(directory, filename):
    """
    Returns the full path to save the file.
    If the file already exists, appends the current timestamp to the filename.
    """
    full_path = os.path.join(directory, filename)
    
    if os.path.exists(full_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_{timestamp}{ext}"
        full_path = os.path.join(directory, new_filename)
        print(f"File exists. Saving as: {new_filename}")
        
    return full_path

def plot_results(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return

    csv_dir = os.path.dirname(csv_path)
    output_dir = os.path.join(csv_dir, "analysis_plots")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Saving plots to: {output_dir}")

    # Convert microseconds to milliseconds/seconds
    df['client_time_ms'] = df['client_time'] / 1000.0
    df['provider_time_ms'] = df['provider_time'] / 1000.0
    df['exec_time_ms'] = df['exec_time'] / 1000.0
    
    # -------------------------------------------------------
    # Cold vs Warm Performance Comparison
    # -------------------------------------------------------
    fig, axes = plt.subplots(1, 2, sharey=False)
    fig.suptitle(f'{BENCHMARK_NAME} {LANGUAGE_NAME} {TITLE_COMMENT} Runtime Performance: Cold vs Warm')

    # Cold Start Plot
    sns.boxplot(ax=axes[0], x="memory", y="client_time_ms", data=df[df['type'] == 'cold'], color="skyblue")
    axes[0].set_title("Cold Start Latency")
    axes[0].set_ylabel("Time (ms)")
    axes[0].set_xlabel("Memory (MB)")
    
    # Warm Execution Plot
    sns.boxplot(ax=axes[1], x="memory", y="client_time_ms", data=df[df['type'] == 'warm'], color="orange")
    axes[1].set_title("Warm Execution Latency")
    axes[1].set_ylabel("Time (ms)")
    axes[1].set_xlabel("Memory (MB)")

    plt.tight_layout()
    
    save_path = get_save_path(output_dir, f"{LANGUAGE_NAME_SAFE}_warm_cold_comparison.png")
    plt.savefig(save_path)
    print(f"Saved: {os.path.basename(save_path)}")

    # -------------------------------------------------------
    # Overhead (Cold Starts Only)
    # -------------------------------------------------------
    plt.figure()
    # Filter for cold starts and valid provider times
    cold_df = df[(df['type'] == 'cold') & (df['provider_time'] > 0)].melt(
        id_vars=['memory'], 
        value_vars=['client_time_ms', 'provider_time_ms', 'exec_time_ms'],
        var_name='Metric', 
        value_name='Time'
    )
    
    sns.barplot(x="memory", y="Time", hue="Metric", data=cold_df, errorbar='sd', palette="muted")
    plt.title(f"{BENCHMARK_NAME} {LANGUAGE_NAME} {TITLE_COMMENT} Overhead (Cold Start)")
    plt.ylabel("Time (ms)")
    plt.tight_layout()
    
    plt.savefig(get_save_path(output_dir, f"{LANGUAGE_NAME_SAFE}_cold_overhead.png"))

    # -------------------------------------------------------
    # Overhead (Warm Starts Only)
    # -------------------------------------------------------
    plt.figure()
    warm_df = df[df['type'] == 'warm'].melt(
        id_vars=['memory'], 
        value_vars=['client_time_ms', 'provider_time_ms', 'exec_time_ms'],
        var_name='Metric', 
        value_name='Time'
    )
    
    sns.barplot(x="memory", y="Time", hue="Metric", data=warm_df, errorbar='sd', palette="muted")
    plt.title(f"{BENCHMARK_NAME} {LANGUAGE_NAME} {TITLE_COMMENT} Overhead (Warm Start): Client/Provider/Exec Time")
    plt.ylabel("Time (ms)")
    
    save_path = get_save_path(output_dir, f"{LANGUAGE_NAME_SAFE}_warm_overhead.png")
    plt.savefig(save_path)
    print(f"Saved: {os.path.basename(save_path)}")

    # -------------------------------------------------------
    # Memory Usage Distribution
    # -------------------------------------------------------
    plt.figure(figsize=(8, 6))
    sns.boxplot(x="memory", y="mem_used", data=df, color="lightgreen")
    plt.ylim(0, df['mem_used'].max() * 1.2)
    plt.title(f"{BENCHMARK_NAME} {LANGUAGE_NAME} {TITLE_COMMENT} Memory Usage Distribution")
    plt.ylabel("Used Memory (MB)")
    plt.xlabel("Allocated Memory (MB)")
    
    save_path = get_save_path(output_dir, f"{LANGUAGE_NAME_SAFE}_memory_usage.png")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Saved: {os.path.basename(save_path)}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, CSV_REL_PATH)
    plot_results(csv_path)