"""Converts a column or row of a CSV into a formatted dynamic arrary for KQL use."""


import argparse
import pandas as pd
import numpy as np



def csv_to_kql_dynamic_array(csv_file, row_index=None, column_name=None):
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)

        if row_index is not None:
            row_values = df.iloc[row_index].dropna().apply(lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x).tolist()
        elif column_name is not None:
            row_values = df[column_name].dropna().tolist()
        else:
            raise ValueError("Either row_index or column_name must be provided")
        
        # Convert to KQL dynamic array format
        kql_array = f'dynamic({row_values})'
        print("\nGenerated KQL dynamic array:\n")
        print(f"\033[92m{kql_array}\033[0m\n\n")
        return kql_array
    except Exception as e:
        print(f"Error: {e}")
        return None
    

def main():
    parser = argparse.ArgumentParser(description="Convert a CSV row or column to a KQL dynamic array.")
    parser.add_argument("file", type=str, help="Path to CSV file.", required=True)
    parser.add_argument("-row", type=int, help="Row ID to extract.", default=None)
    parser.add_argument("-column", type=str, help="Column name to extract.", default=None)

    args = parser.parse_args()

    if args.row is None and args.column is None:
        print("Error: Either a row index (-r) or column name (-c) must be supplied.")
        return
    
    csv_to_kql_dynamic_array(args.csv_file, args.row, args.column)

if __name__ == "__main__":
    main()
