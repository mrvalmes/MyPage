import pandas as pd
import sys

# Read the Excel file to inspect the subcanal column
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    print("Usage: python inspect_excel.py <path_to_excel_file>")
    print("\nPlease provide the path to your sales Excel file")
    sys.exit(1)

try:
    df = pd.read_excel(file_path, header=9, usecols="B:BM")
    
    print("=== Excel File Inspection ===\n")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}\n")
    
    print("Column names:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    
    if 'subcanal' in df.columns:
        print("\n=== Subcanal Column Analysis ===")
        print(f"Data type: {df['subcanal'].dtype}")
        print(f"Unique values count: {df['subcanal'].nunique()}")
        print(f"\nFirst 10 unique values:")
        print(df['subcanal'].unique()[:10])
        
        # Check for non-numeric values
        non_numeric = df[pd.to_numeric(df['subcanal'], errors='coerce').isna() & df['subcanal'].notna()]
        if len(non_numeric) > 0:
            print(f"\n⚠️  Found {len(non_numeric)} non-numeric values in subcanal:")
            print(non_numeric['subcanal'].unique()[:20])
    else:
        print("\n⚠️  Column 'subcanal' not found in Excel file")
        
except Exception as e:
    print(f"Error reading Excel file: {e}")
