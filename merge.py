import os
import glob
import pandas as pd

def combine_pr_and_ghi(root_dir: str, output_file: str = "merged_PR_GHI.csv"):

    # --- Locate all relevant files ---
    pr_paths = glob.glob(os.path.join(root_dir, "PR", "**", "*.csv"), recursive=True)
    ghi_paths = glob.glob(os.path.join(root_dir, "GHI", "**", "*.csv"), recursive=True)
    print(f"Located {len(pr_paths)} PR files and {len(ghi_paths)} GHI files.")

    # --- Load and unify PR datasets ---
    pr_frames = []
    for path in pr_paths:
        temp = pd.read_csv(path)
        if 'PR' not in temp.columns:
            temp.columns = ['Date', 'PR']
        pr_frames.append(temp)
    pr_data = pd.concat(pr_frames, ignore_index=True)
    pr_data['Date'] = pd.to_datetime(pr_data['Date'])
    pr_data = pr_data.drop_duplicates(subset='Date')

    # --- Load and unify GHI datasets ---
    ghi_frames = []
    for path in ghi_paths:
        temp = pd.read_csv(path)
        if 'GHI' not in temp.columns:
            temp.columns = ['Date', 'GHI']
        ghi_frames.append(temp)
    ghi_data = pd.concat(ghi_frames, ignore_index=True)
    ghi_data['Date'] = pd.to_datetime(ghi_data['Date'])
    ghi_data = ghi_data.drop_duplicates(subset='Date')

    # --- Merge PR and GHI on Date ---
    merged_df = pd.merge(ghi_data, pr_data, on='Date', how='inner').sort_values('Date')

    # --- Save the merged file ---
    merged_df.to_csv(output_file, index=False)
    print(f"\n✅ Data successfully merged and saved as '{output_file}'")
    print(f"Total rows combined: {len(merged_df)}")
    print(merged_df.head())

    return merged_df


# Example run
if __name__ == "__main__":
    combine_pr_and_ghi("data")
