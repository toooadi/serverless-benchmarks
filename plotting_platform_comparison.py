import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import argparse
from datetime import datetime

sns.set_theme(style="whitegrid")
plt.rcParams.update({'figure.figsize': (10, 6)})

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

def load_and_prep_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return None

    # Convert microseconds to milliseconds
    df['client_time_ms'] = df['client_time'] / 1000.0
    if 'exec_time' in df.columns:
        df['exec_time_ms'] = df['exec_time'] / 1000.0
    return df

def plot_platform_comparison(aws_csv_path, gcp_csv_path):
    aws_df = load_and_prep_data(aws_csv_path)
    gcp_df = load_and_prep_data(gcp_csv_path)

    if aws_df is None or gcp_df is None:
        return

    # Use directory of the AWS CSV for output (arbitrary choice, but follows previous logic)
    csv_dir = os.path.dirname(aws_csv_path)
    output_dir = os.path.join(csv_dir, "analysis_plots")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Saving plots to: {output_dir}")

    # -------------------------------------------------------
    # Warm vs Warm Performance Comparison
    # -------------------------------------------------------
    fig, axes = plt.subplots(1, 2, sharey=True) # Share Y axis makes comparison easier
    fig.suptitle(f'Warm Start Performance Comparison')

    # AWS Plot (Left)
    sns.boxplot(ax=axes[0], x="memory", y="client_time_ms", data=aws_df[aws_df['type'] == 'warm'], color="orange")
    axes[0].set_title("AWS")
    axes[0].set_ylabel("Time (ms)")
    axes[0].set_xlabel("Memory (MB)")
    
    # GCP Plot (Right)
    sns.boxplot(ax=axes[1], x="memory", y="client_time_ms", data=gcp_df[gcp_df['type'] == 'warm'], color="orange")
    axes[1].set_title("GCP")
    axes[1].set_ylabel("") # Hide y label for second plot as they share Y
    axes[1].set_xlabel("Memory (MB)")

    plt.tight_layout()
    
    save_path = get_save_path(output_dir, "platform_warm_comparison.png")
    plt.savefig(save_path)
    print(f"Saved: {os.path.basename(save_path)}")

    # -------------------------------------------------------
    # Overhead (Warm Starts Only) - Client vs Exec
    # -------------------------------------------------------
    fig2, axes2 = plt.subplots(1, 2, sharey=True)
    fig2.suptitle(f'Warm Overhead Comparison (Client vs Exec)')

    # Prepare data for AWS (Left)
    if 'exec_time_ms' in aws_df.columns:
        warm_aws = aws_df[aws_df['type'] == 'warm'].melt(
            id_vars=['memory'], 
            value_vars=['client_time_ms', 'exec_time_ms'],
            var_name='Metric', 
            value_name='Time'
        )
        sns.barplot(ax=axes2[0], x="memory", y="Time", hue="Metric", data=warm_aws, errorbar='sd', palette="muted")
    else:
        axes2[0].text(0.5, 0.5, "Exec time not found", ha='center')
        
    axes2[0].set_title("AWS")
    axes2[0].set_ylabel("Time (ms)")
    
    # Prepare data for GCP (Right)
    if 'exec_time_ms' in gcp_df.columns:
        warm_gcp = gcp_df[gcp_df['type'] == 'warm'].melt(
            id_vars=['memory'], 
            value_vars=['client_time_ms', 'exec_time_ms'],
            var_name='Metric', 
            value_name='Time'
        )
        sns.barplot(ax=axes2[1], x="memory", y="Time", hue="Metric", data=warm_gcp, errorbar='sd', palette="muted")
    else:
        axes2[1].text(0.5, 0.5, "Exec time not found", ha='center')

    axes2[1].set_title("GCP")
    axes2[1].set_ylabel("")
    
    plt.tight_layout()
    save_path_overhead = get_save_path(output_dir, "platform_warm_overhead.png")
    plt.savefig(save_path_overhead)
    print(f"Saved: {os.path.basename(save_path_overhead)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare warm starts from AWS and GCP results CSVs.")
    parser.add_argument("aws_csv_path", help="Path to the AWS results.csv")
    parser.add_argument("gcp_csv_path", help="Path to the GCP results.csv")
    
    args = parser.parse_args()
    
    plot_platform_comparison(args.aws_csv_path, args.gcp_csv_path)