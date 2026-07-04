#!/usr/bin/env python3
"""Update QC Dashboard Data from Excel to JSON"""

import pandas as pd
import json
import os

EXCEL_FILE = r'C:\Users\panup\The Siam Cement Public Company Limited\B-26-6530_RISE Project - STC-REPCO\1.STC to REPCO\5.Others\RISE_Overall RFI_FIR  Summary\RISE_Overall RFI_FIR  Summary.xlsx'
JSON_FILE = r'D:\Daily Report\Rise-dashboard\Data\qc_data.json'

def update_qc_data():
    try:
        print("📖 Reading QC Log Excel file...")

        # Read Summary sheet (A5:K12) - with proper header
        print("📄 Reading Summary RISE RFI&FIR sheet...")
        summary_df = pd.read_excel(EXCEL_FILE, sheet_name='Summary RISE RFI&FIR', header=4, usecols='A:K', nrows=8)
        summary_df = summary_df.dropna(how='all')

        print(f"📄 Summary data shape: {summary_df.shape}")
        print(f"📄 Summary columns: {list(summary_df.columns)}")
        print(f"📄 Summary data:")
        print(summary_df.to_string())

        # Read RFI sheet (Row 3 as header)
        print("📄 Reading RISE RFI&FIR sheet...")
        rfi_full = pd.read_excel(EXCEL_FILE, sheet_name='RISE RFI&FIR', header=2)

        # Process Summary data - extract Total row only
        print(f"\n📄 Finding Total row...")
        summary_df_clean = summary_df.fillna('')

        # Find row with 'Total' in first column
        total_row = None
        for idx, row in summary_df_clean.iterrows():
            if 'Total' in str(row.iloc[1]) if len(row) > 1 else False:  # Check Discipline column
                total_row = row
                print(f"✓ Found Total row at index {idx}")
                break

        if total_row is None:
            print("⚠️ Warning: Total row not found, using last row")
            total_row = summary_df_clean.iloc[-1]

        print(f"✓ Total row data: {total_row.to_dict()}")
        summary_data = [total_row.to_dict()]  # Only Total row

        # Process RFI data - use all rows (no filter)
        print(f"📄 Using all RFI data (no filter)...")
        rfi_accepted = rfi_full.copy()

        # Keep all data as-is from Excel
        # The first column should already be 'No.' from Column A in Excel
        rfi_data_clean = rfi_accepted.reset_index(drop=True)

        print(f"📄 Total RFI records: {len(rfi_data_clean)}")
        print(f"📄 First column: {rfi_data_clean.columns[0]}")
        if len(rfi_data_clean) > 0:
            print(f"📄 First 5 rows (Column A - No.):")
            for i in range(min(5, len(rfi_data_clean))):
                print(f"  Row {i+1}: {rfi_data_clean.iloc[i, 0]}")
            print(f"📄 Last 2 rows:")
            for i in range(max(0, len(rfi_data_clean)-2), len(rfi_data_clean)):
                print(f"  Row {i+1}: {rfi_data_clean.iloc[i, 0]}")

        # First, let's see all column names to identify correct indices
        print("📄 All columns in Excel:")
        for i, col in enumerate(rfi_data_clean.columns):
            print(f"  [{i}] {col}")

        print("\n📄 Selecting columns A, E, F, I, J, AE...")

        # Column indices (0-based)
        selected_indices = [0, 4, 5, 8, 9, 30]  # A, E, F, I, J, AE

        # Check if indices are valid
        valid_indices = [idx for idx in selected_indices if idx < len(rfi_data_clean.columns)]

        print(f"✓ Valid indices: {valid_indices}")

        if len(valid_indices) < 6:
            print(f"⚠️ Warning: Only {len(valid_indices)} columns available out of 6 requested")
            # Try without Column AE (index 30)
            selected_indices = [0, 4, 5, 8, 9]
            valid_indices = [idx for idx in selected_indices if idx < len(rfi_data_clean.columns)]
            print(f"✓ Fallback to 5 columns: {valid_indices}")

        # Create filtered dataframe with selected columns
        rfi_filtered = rfi_data_clean.iloc[:, valid_indices].copy()

        # Set new column names
        column_names = [
            'No.',
            'RFI No.',
            'Planned Inspection Date',
            'ITP Description',
            'Description of Inspection',
            'Inspection Result'
        ]

        # Trim to match available columns
        rfi_filtered.columns = column_names[:len(rfi_filtered.columns)]

        print(f"✓ Selected {len(rfi_filtered)} RFI items")
        print(f"✓ Columns: {list(rfi_filtered.columns)}")

        # Convert datetime to string
        for col in rfi_filtered.columns:
            if rfi_filtered[col].dtype == 'object':
                try:
                    rfi_filtered[col] = pd.to_datetime(rfi_filtered[col], errors='coerce')
                except:
                    pass

        # Convert all datetime columns to string
        for col in rfi_filtered.columns:
            if str(rfi_filtered[col].dtype).startswith('datetime'):
                rfi_filtered[col] = rfi_filtered[col].dt.strftime('%Y-%m-%d').where(pd.notna(rfi_filtered[col]), '')

        rfi_filtered = rfi_filtered.fillna('')
        rfi_data = rfi_filtered.to_dict(orient='records')

        # Combine data
        rfi_columns = list(rfi_filtered.columns) if 'rfi_filtered' in locals() else []
        data = {
            'summary': summary_data,
            'rfi_open': rfi_data,
            'summary_columns': list(summary_df.columns),
            'rfi_columns': rfi_columns
        }

        # Save to JSON
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Saved {len(summary_data)} summary records")
        print(f"✓ Saved {len(rfi_data)} open RFI records")
        print(f"✓ File: {JSON_FILE}")

        # Statistics
        print(f"\n📊 Statistics:")
        print(f"  Summary Disciplines: {len(summary_data)}")
        print(f"  Open RFI Items: {len(rfi_data)}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("QC Dashboard Data Updater")
    print("=" * 60)
    print()

    success = update_qc_data()

    print()
    if success:
        print("✓ Update completed successfully!")
        print("➜ Open dashboard to see the latest data")
    else:
        print("❌ Update failed. Check error messages above.")

    print()
    input("Press Enter to close...")
